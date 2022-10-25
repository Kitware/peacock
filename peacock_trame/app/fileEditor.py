# existing backend imports
from .core.input.InputTree import InputTree
from .core.input.ExecutableInfo import ExecutableInfo

from pyaml import yaml
from bisect import insort
import os

from trame.widgets import vuetify, vtk, html, simput
from trame_simput import get_simput_manager
from trame_simput.core.mapping import ProxyObjectAdapter, ObjectFactory

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)
from vtkmodules.vtkIOExodus import vtkExodusIIReader
from vtkmodules.vtkFiltersGeometry import vtkCompositeDataGeometryFilter
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa


class InputFileEditor:
    def __init__(self, server, simput_manager):
        self._server = server
        state = server.state

        self.block_path_map = {}  # map of block ids to name
        self.cpp_type_map = {
            'bool': 'bool',
            'char': 'int8',
            'unsigned char': 'uint8',
            'short': 'int16',
            'unsigned short': 'uint16',
            'int': 'int32',
            'unsigned int': 'uint32',
            'long': 'int64',
            'unsigned long': 'uint64',
            'float': 'float32',
            'double': 'float64',
            'std::string': 'string',
        }

        state.add_block_open = False
        state.active_id = 1
        state.show_mesh = False
        state.block_to_add = None
        state.child_types = {}  # map of possible children types for each block

        state.change('active_id')(self.on_active_id)
        state.change('block_to_add')(self.on_block_to_add)

        exe_info = ExecutableInfo()
        exe_info.setPath(state.executable)
        self.tree = InputTree(exe_info)

        self.populate_simput_model(simput_manager)
        self.set_input_file(state.input_file)

    def set_input_file(self, file_name):
        # sets the input file of the InputTree object and populates simput/ui

        state = self._server.state
        self.block_tree = []  # list of tree entries as used by vuetify's vtreeview
        self.unused_blocks = []  # unused parent block names
        state.block_tree = self.block_tree
        state.unused_blocks = self.unused_blocks

        self.tree.setInputFile(file_name)

        # --- populate input file tree ---
        root_block = self.tree.getBlockInfo('/')
        for path, block in root_block.children.items():
            if block.included:
                self.add_block(block)
            else:
                insort(self.unused_blocks, {'name': block.name, 'path': block.path}, key=lambda e: e['name'])

    def write_file(self):
        # write input file tree to disk

        path = self._server.state.input_file
        print(f"Writing to {path}...")
        with open(path, 'w') as f:
            f.write(self.tree.getInputFileString())
        print("done")

    def populate_simput_model(self, simput_manager):
        # creates a simput model from all of the block in the InputTree object

        # --- create simput model ---
        block_model = {}
        for path, block in self.tree.path_map.items():
            if path == '/':  # skip root
                continue

            # accumulate simput types to create for this block
            type_list = []
            # add each type this block can be
            for type_name, type_info in block.types.items():
                type_list.append(type_info)
            # add the block itself if it has no types
            if len(type_list) == 0:
                type_list.append(block)
            # add each type from its star node
            star_node = block.star_node
            if star_node:
                for type_name, type_info in star_node.types.items():
                    type_list.append(type_info)

            # create simput types
            for type_info in type_list:
                params = type_info.orderedParameters()

                # add block parameters if it is a type of this block
                if type_info.parent.name == block.name:
                    params = params + block.orderedParameters()

                params_dict = {}
                for param in params:
                    params_dict[param.name] = self.format_simput_param(param)

                # sort params so that:
                #  - type is 1st
                #  - all required follows
                #  - everything else is alphabetical
                params_dict = dict(sorted(params_dict.items(), key=lambda kv: (kv[0] != 'type', kv[1]['required'] == False, kv[0])))

                block_model[type_info.name] = params_dict

        output_file = self._server.state.model_file
        if output_file:
            print("writing model file...")
            with open('model.yaml', 'w') as f:
                yaml.dump(block_model, f, sort_keys=False)
            print("done")

        print("dumping yaml...")
        yaml_str = yaml.dump(block_model, sort_keys=False)
        print("loading model...")
        simput_manager.load_model(yaml_content=yaml_str)
        print("model loaded")
        self.pxm = simput_manager.proxymanager

    def add_block(self, block):
        # Adds block and all children to vuetify block tree and simput

        # --- create simput entry ---
        simput_type = block.name
        # vals = {}
        params = block.orderedParameters()

        type_block = block.getTypeBlock()
        if type_block is None and len(block.types) > 0:
            # use first type as default
            default_type = list(block.types)[0]
            block.setBlockType(default_type)
            type_block = block.getTypeBlock()

        if type_block is not None:
            params = params + type_block.orderedParameters()
            simput_type = type_block.name


        simput_entry = self.pxm.create(simput_type, existing_obj=block)
        block_id = int(simput_entry.id)
        self.block_path_map[block_id] = block.path

        # --- add to vuetify tree ---
        block_entry = {
            "id": block_id,
            "name": block.name,
            "path": block.path,
        }

        # check if block is a child
        parent = block.parent
        if parent.path == '/':  # no parent
            # add block to tree sorted by name
            insort(self.block_tree, block_entry, key=lambda e: e['name'])
        else:
            # path is in form /ancestor_a/ancestor_b/.../parent/block
            # splitting by '/' gives ['', ancestor_a, ancestor_b, ... ,parent, block]
            ancestors = block.path.split('/')[0:-1]
            block_list = self.block_tree
            # find block in tree
            for ancestor in ancestors:
                for b in block_list:
                    if b['name'] == ancestor:
                        if 'children' not in b:
                            b['children'] = []
                        block_list = b['children']
                        parent_entry = b

            parent_entry['children'].append(block_entry)

        star_node = block.star_node
        if star_node:
            child_types = list(star_node.types.keys())
        else:
            child_types = []
        state = self._server.state
        state.child_types[block.name] = child_types

        # add children
        for _, child in block.children.items():
            self.add_block(child)

    # TODO: implement this
    def remove_block(self, block):
        return

    def add_child_block(self, parent, child_type):
        parent_info = self.tree.getBlockInfo('/' + parent)
        new_name = parent_info.findFreeChildName()
        new_block = self.tree.addUserBlock(parent_info.path, new_name)
        self.add_block(new_block)
        self.update_state()

    def format_simput_param(self, param):
        # formats a simput property from a ParameterInfo object for use in the simput model

        # strip vector wrapping from cpp type
        # TODO: handle matrices
        cpp_type = param.cpp_type
        cpp_type = cpp_type.split('std::vector<')[-1]
        cpp_type = cpp_type.split('>')[0]

        try:
            simput_type = self.cpp_type_map[cpp_type]
        except KeyError:
            # if the c++ type is not in the map, we assume it is a Moose object type and map it to string
            # simput_type = param.basic_type.split('Array:')[-1]
            simput_type = 'string'

        param_entry = {
            '_label': param.name,
            '_help': param.toolTip(),
            'type': simput_type,
            'initial': param.getValue(),
            'required': param.required,
        }

        if param.options:
            if 'domains' not in param_entry:
                param_entry['domains'] = []
            param_entry['domains'].append(
                {
                    'type': 'LabelList',
                    'values': [{'text': val, 'value': val} for val in param.options]
                }
            )

        if param.isVectorType():
            if 'domains' not in param_entry:
                param_entry['domains'] = []
            param_entry['domains'].append(
                {
                    'type': 'UI',
                    'properties': {
                        'sizeControl': 1
                    }
                }
            )

            # use indeterminate size for arrays
            # TODO: handle matrices
            param_entry['size'] = -1

        return param_entry

    def on_active_id(self, active_id, **kwargs):
        # this function triggers when a block is selected from the tree in the ui

        state = self._server.state

        if active_id is None:
            return

        active_block = self.tree.getBlockInfo(self.block_path_map[active_id])

        state.show_mesh = active_block.name == 'Mesh' or active_block.parent.name == 'Mesh'

        state.active_types = list(active_block.types.keys())
        state.active_type = active_block.blockType()

    def on_active_type(self, active_type, **kwargs):
        state = self._server.state
        pxm = self.pxm

        active_id = state.active_id
        active_block = self.tree.getBlockInfo(self.block_path_map[active_id])
        active_block.setBlockType(active_type)

        pxm.delete(active_id)

        pxm._obj_factory.next(active_block)
        pxm.create(active_type, proxy_id=active_id)

    def on_block_to_add(self, block_to_add, **kwargs):
        # this function triggers when a new block is added to the tree in the ui

        if block_to_add is None:
            return

        state = self._server.state

        # remove from unused_blocks
        for block_idx, block in enumerate(self.unused_blocks):
            if block['path'] == block_to_add:
                self.unused_blocks.pop(block_idx)

        # add to block tree
        block = self.tree.getBlockInfo(block_to_add)
        self.add_block(block)

        self.update_state()

    def update_state(self):
        # update trame server state to align with self

        state = self._server.state
        state.unused_blocks = self.unused_blocks
        state.block_tree = self.block_tree
        state.dirty('unused_blocks')
        state.dirty('block_tree')

    def get_ui(self):
        # return ui for input file editor

        ctrl = self._server.controller
        input_ui = vuetify.VContainer(
            fluid=True,
            classes="fill-height flex-nowrap d-flex ma-0 pa-0",
            style="position: relative;"
        )

        with input_ui:
            with html.Div(classes="fill-height d-flex flex-column"):
                with vuetify.VTreeview(
                    v_if="block_tree.length > 0",
                    items=("block_tree",),
                    style="width: 300px; flex: 1 1 0px; overflow: auto;",
                    hoverable=True,
                    rounded=True,
                    activatable=True,
                    active=("active_ids", [1]),
                    update_active="(active_ids) => {active_id = active_ids[0]}"
                ):
                    with vuetify.Template(v_slot_label="{ item }"):
                        with html.Div(classes="d-flex justify-space-between align-center"):
                            html.P("{{item.name}}", classes="ma-0")

                            vuetify.VSpacer()

                            with vuetify.VMenu():
                                with vuetify.Template(v_slot_activator="{on, attrs}",):
                                    with vuetify.VBtn(
                                        v_if="child_types[item.name].length > 0",
                                        icon=True,
                                        v_on="on", v_bind="attrs",
                                        click="(event) => {event.stopPropagation(); event.preventDefault();}"
                                    ):
                                        vuetify.VIcon("mdi-plus-circle",)

                                with vuetify.VList():
                                    vuetify.VListItem(
                                        "{{child_type}}",
                                        v_for="child_type in child_types[item.name]",
                                        click=(self.add_child_block, "[item.name, child_type]"),
                                    )

                            with vuetify.VBtn(icon=True, click="""
                                (event) => {
                                    event.preventDefault(); event.stopPropagation();
                                    let item_idx = block_tree.findIndex( (e) => e.name == item.name);
                                    block_tree = block_tree.slice(0, item_idx).concat(block_tree.slice(item_idx+1));
                                    unused_blocks.push(item);
                                }"""
                            ):
                                vuetify.VIcon("mdi-delete")

                with vuetify.VContainer(fluid=True, style="width: 100%; padding: 10px;"):
                    with vuetify.VBtn(v_if="!add_block_open", click="add_block_open=true", style="width: 100%;"):
                        vuetify.VIcon('mdi-plus-circle')

                    with vuetify.VBtn(v_if="add_block_open", click="add_block_open=false", style="width: 100%;"):
                        vuetify.VIcon("mdi-close-circle")
                        html.P("Cancel", classes="ma-0")

                with vuetify.VContainer(v_if="add_block_open", style="overflow-y: auto; flex: 1 1 0px; width: calc(100% - 20px);", classes="d-flex flex-column"):
                    with vuetify.VList():
                        vuetify.VListItem("{{block.name}}", v_for="block in unused_blocks", click="block_to_add = block.path; add_block_open = false;")

            with vuetify.VContainer(
                fluid=True,
                classes="fill-height d-flex flex-column flex-nowrap",
            ):
                with vuetify.VContainer(
                    v_if="show_mesh",
                    style="height: 50%;",
                ):
                    vtk.VtkRemoteView(
                        self.create_vtk_render_window(),
                    )

                with vuetify.VCol(
                    style="overflow: auto;"
                ):
                    vuetify.VCombobox(
                        v_model=("active_type",),
                        v_if="active_type != null",
                        items=("active_types",),
                        label="Type",
                        change=(self.on_active_type, "[$event]"),
                    )
                    simput.SimputItem(item_id=("active_id",))

        return input_ui

    def create_vtk_render_window(self):
        mesh_file_name = self.tree.getParamInfo('/Mesh', 'file').getValue()

        reader = vtkExodusIIReader()
        reader.SetFileName(mesh_file_name)
        reader.UpdateInformation()
        reader.SetTimeStep(10)
        reader.SetAllArrayStatus(vtkExodusIIReader.NODAL, 1)  # enables all NODAL variables
        reader.Update()

        geometry = vtkCompositeDataGeometryFilter()
        geometry.SetInputConnection(0, reader.GetOutputPort(0))
        geometry.Update()

        mapper = vtkPolyDataMapper()
        mapper.SetInputData(geometry.GetOutput())

        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()

        renderer = vtkRenderer()
        renderer.AddActor(actor)

        renderWindow = vtkRenderWindow()
        renderWindow.AddRenderer(renderer)
        renderWindow.SetOffScreenRendering(1)

        interactor = vtkRenderWindowInteractor()
        interactor.SetRenderWindow(renderWindow)
        interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        return renderWindow

class BlockFactory(ObjectFactory):
    def __init__(self):
        self._block = None

    def next(self, obj):
        self._block = obj

    def create(self, name, **kwargs):
        obj = self._block
        self._block = None

        return obj

class BlockAdapter(ProxyObjectAdapter):

    @staticmethod
    def commit(proxy):
        pass

    @staticmethod
    def reset(proxy, props_to_reset=[]):
        block = proxy.object
        for name in props_to_reset:
            value = proxy[name]
            block.setParamValue(name, value)

    @staticmethod
    def fetch(proxy):
        block = proxy.object
        change_set = {}
        for name in proxy.list_property_names():
            value = block.paramValue(name)
            change_set[name] = value

        proxy.state = {"properties": change_set}

    @staticmethod
    def update(proxy, *property_names):
        block = proxy.object
        for name in property_names:
            value = proxy[name]
            block.setParamValue(name, value)

    @staticmethod
    def before_delete(proxy):
        pass