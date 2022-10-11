# existing backend imports
from ..core.input.InputTree import InputTree
from ..core.input.ExecutableInfo import ExecutableInfo

from pyaml import yaml

from trame.widgets import vuetify, vtk, html
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
    def __init__(self, server):
        self._server = server
        state = server.state

        state.active_block = 'Mesh'
        state.add_new_block = False

        state.change('active_block')(self.on_active_block)

        exe_info = ExecutableInfo()
        exe_info.setPath(state.executable)
        self.tree = InputTree(exe_info)

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

        block_model = {}
        for path, block in self.tree.path_map.items():
            block_params = block.orderedParameters()
            for type_name, type_info in block.types.items():
                type_params = type_info.orderedParameters() + block_params

                params_dict = {}
                for param in type_params:
                    params_dict[param.name] = self.format_simput_param(param)

                block_model[type_name] = params_dict

        with open('model.yaml', 'w') as f:
            yaml.dump(block_model, f)

        self.tree.setInputFile(state.input_file)

        # --- populate input file tree ---
        block_tree = []  # list of tree entries as used by vuetify's vtreeview
        unused_blocks = []  # unused parent block names

        root_block = self.tree.getBlockInfo('/')
        for path, block in root_block.children.items():

            block_entry = {
                "name": block.name,
            }

            if len(block.children) > 0:
                block_entry['children'] = [
                    {
                        "name": block.name,
                    }
                    for path, block in block.children.items()
                ]

            if block.included:
                block_tree.append(block_entry)
            else:
                unused_blocks.append(block_entry)

        self.block_tree = block_tree
        self.unused_blocks = unused_blocks

        state.block_tree = block_tree
        state.unused_blocks = unused_blocks

    def format_simput_param(self, param):

        cpp_type = param.cpp_type

        # use indeterminate size if param is vector
        # TODO: handle matrices
        if cpp_type.startswith('std::vector'):
            size = -1
        else:
            size = 1

        cpp_type = cpp_type.split('std::vector<')[-1]
        cpp_type = cpp_type.split('>')[0]

        try:
            simput_type = self.cpp_type_map[cpp_type]
        except KeyError:
            # if the c++ type is not in the map, we assume it is a Moose object type
            # use the basic type
            simput_type = param.basic_type.split('Array:')[-1]

        return {
            '_label': param.name,
            'type': simput_type,
            'size': size,
        }

    def on_active_block(self, active_block, **kwargs):

        # find block in tree
        for block in self.block_tree:
            if block['name'] == active_block:
                block_path = '/' + active_block
                break

            if 'children' in block:
                for child in block['children']:
                    if child['name'] == active_block:
                        block_path = '/' + block['name'] + '/' + active_block
                        break

        block = self.tree.getBlockInfo(block_path)

        try:
            block_type = block.parameters['type'].value
            type_info = block.types[block_type]
            all_params = block.orderedParameters() + type_info.orderedParameters()
        except KeyError:
            all_params = block.orderedParameters()

        params = []
        for param in all_params:
            params.append({
                "name": param.name,
                "value": param.value,
                "default": param.default,
                "parent": param.parent.path,
                "required": param.required,
                "type": param.basic_type,
                "cpp_type": param.cpp_type,
                "description": param.description,
                "comments": param.comments,
                "group": param.group_name,
                "options": param.options,
                "user_added": param.user_added,
                "set_in_input_file": param.set_in_input_file,
            })

            params = sorted(params, key=lambda p: 1 - p['required'])

        self._server.state.params = params

    def get_ui(self):
        input_ui = vuetify.VContainer(
            fluid=True,
            classes="fill-height flex-nowrap d-flex ma-0 pa-0",
            style="position: relative;"
        )
        with input_ui:
            # with trame.FloatCard(style="position: absolute; max-height: 50%; overflow-y: auto;", location=("[0, 0]",),):
            with html.Div(classes="fill-height d-flex flex-column"):
                with vuetify.VTreeview(
                    v_if="block_tree.length > 0",
                    items=("block_tree",),
                    style="width: 300px;",
                    hoverable=True,
                    rounded=True,
                    activatable=True,
                    active=("active_blocks", ['Mesh'],),  # default to mesh view
                    item_key="name",
                    update_active="(active_blocks) => {active_block = active_blocks[0]}"
                ):
                    with html.Template(v_slot_label="{ item }"):
                        with html.Div(classes="d-flex justify-space-between align-center"):
                            html.P("{{item.name}}", classes="ma-0")
                            with vuetify.VBtn(icon=True, click="""
                                (event) => {
                                    event.preventDefault(); event.stopPropagation();
                                    let item_idx = block_tree.findIndex( (e) => e.name == item.name);
                                    block_tree = block_tree.slice(0, item_idx).concat(block_tree.slice(item_idx+1));
                                    unused_blocks.push(item);
                                }"""
                            ):
                                vuetify.VIcon("mdi-delete")

                with vuetify.VBtn(v_if="!add_new_block", click="add_new_block=true"):
                    vuetify.VIcon('mdi-plus-circle')

                with vuetify.VBtn(v_if="add_new_block", click="add_new_block=false"):
                    vuetify.VIcon("mdi-close-circle")
                    html.P("Cancel", classes="ma-0")

                with vuetify.VContainer(v_if="add_new_block", style="overflow-y: auto; flex: 1 1 0px; margin: 10px; width: calc(100% - 20px);", classes="elevation-10 d-flex flex-column"):
                    vuetify.VBtn("{{block.name}}", v_for="block in unused_blocks", click="""
                        () => {
                            let block_idx = unused_blocks.findIndex((e) => e.name == block.name);
                            unused_blocks = unused_blocks.slice(0, block_idx).concat(unused_blocks.slice(block_idx+1));
                            block_tree = block_tree.concat([block]);
                            add_new_block=false;
                        }"""
                    )

            with vuetify.VContainer(
                fluid=True,
                classes="fill-height d-flex flex-column flex-nowrap",
            ):
                with vuetify.VContainer(
                    v_if="active_block == 'Mesh'",
                    # classes="flex-grow-1",
                    style="height: 50%;",
                ):
                    vtk.VtkRemoteView(
                        self.create_vtk_render_window(),
                    )

                with vuetify.VContainer(
                    fluid=True,
                    style="overflow: auto; flex: 1 1 0px;"
                ):
                    with vuetify.VRow(v_for="param in params"):
                        vuetify.VCol("{{param.name}}")
                        vuetify.VCol("{{param.value}}")

        return input_ui

    def create_vtk_render_window(self):
        mesh_file_name = self.tree.getParamInfo('/Mesh', 'file').value

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
