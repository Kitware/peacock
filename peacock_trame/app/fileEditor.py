import difflib
import os
import sys
from pathlib import Path

import vtkmodules.vtkRenderingOpenGL2  # noqa
from pyaml import yaml
from trame.widgets import html, paraview, simput, vtk, vuetify
from trame_simput.core.mapping import ObjectFactory, ProxyObjectAdapter
from vtkmodules.vtkFiltersExtraction import vtkExtractBlock
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
from vtkmodules.vtkIOExodus import vtkExodusIIReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from peacock_trame.widgets import peacock

from .core.common.PeacockException import BadExecutableException
from .core.common.utils import debounced_run

# add moose/python to sys path
conda_prefix = os.environ.get("CONDA_PREFIX", None)
if conda_prefix:
    lib_path = Path(conda_prefix) / "moose/share/moose/python"
    if lib_path.exists():
        sys.path.append(str(lib_path))

from .core.common import ExeLauncher  # noqa
from .core.input.ExecutableInfo import ExecutableInfo  # noqa
from .core.input.InputTree import InputTree  # noqa

try:
    from paraview import simple

    USE_PARAVIEW = True
except ModuleNotFoundError:
    USE_PARAVIEW = False
print("USE_PARAVIEW: ", USE_PARAVIEW)


class InputFileEditor:
    def __init__(self, server, simput_manager):
        self._server = server
        state = server.state

        self.cpp_type_map = {
            "bool": "bool",
            "char": "int8",
            "unsigned char": "uint8",
            "short": "int16",
            "unsigned short": "uint16",
            "int": "int32",
            "unsigned int": "uint32",
            "long": "int64",
            "unsigned long": "uint64",
            "float": "float32",
            "double": "float64",
            "std::string": "string",
        }

        state.add_block_open = False
        state.active_id = "/Mesh_type_/Mesh/FileMesh"
        state.active_name = "Mesh"
        state.name_editable = False
        state.show_mesh = False
        state.show_file_editor = False
        state.block_to_add = None
        state.block_to_remove = None
        state.bc_boundaries = {}

        state.change("active_id")(self.on_active_id)
        state.change("block_to_add")(self.on_block_to_add)
        state.change("block_to_remove")(self.on_block_to_remove)

        exe_info = ExecutableInfo()
        exe_info.setPath(state.executable)
        self.tree = InputTree(exe_info)
        self.simput_types = []
        self.simput_manager = simput_manager
        self.pxm = simput_manager.proxymanager
        self.updating_from_editor = False
        self.vtkRenderWindow = None
        self.vtkRenderer = None
        self.set_input_file(file_name=state.input_file)
        self.update_editor()

        self.pxm.on(self.on_proxy_change)

    def toggle_editor(self):
        # open monaco file editor if it is closed and visa versa
        state = self._server.state
        state.show_file_editor = not state.show_file_editor

    def update_editor(self):
        state = self._server.state
        state.file_str = self.tree.getInputFileString()
        state.flush()

    def on_proxy_change(self, topic, ids=None, **kwargs):
        state = self._server.state

        # only update when change comes from simput
        if not self.updating_from_editor:
            # debounce to prevent running on each user input, bogs down the server
            debounced_run(self.update_editor, delay=0.5)

            for proxy_id in ids:
                if (
                    "/Mesh_type" in proxy_id
                ):  # update render window if mesh updated from simput
                    # debounce to prevent running on each user input, bogs down the server
                    debounced_run(self.update_render_window, delay=0.5)
                elif state.bc_selected:  # check if new boundaries added to BC
                    block_path = state.active_id.split("_type_")[0]
                    active_block = self.tree.getBlockInfo(block_path)

                    boundaries = active_block.paramValue("boundary")
                    for boundary_id in boundaries:
                        if (
                            boundary_id not in state.bc_boundaries
                            and boundary_id in state.boundaries
                        ):
                            info = state.boundaries[boundary_id].copy()
                            info["visible"] = True
                            self.vtkMappers["boundaries"].SetBlockVisibility(
                                info["index"], True
                            )
                            state.bc_boundaries[boundary_id] = info
                            state.dirty("bc_boundaries")
                            self.vtkRenderWindow.Render()
                            self._server.controller.update_input_mesh_view()

    def set_input_file(self, file_name=None, file_str=None):
        # sets the input file of the InputTree object and populates simput/ui

        if file_name:
            valid = self.tree.setInputFile(file_name)
        else:
            valid = self.tree.setInputFileData(file_str)

        if not valid:
            return False

        state = self._server.state
        state.block_tree = []  # list of tree entries as used by vuetify's vtreeview
        state.unused_blocks = []  # unused parent block names

        # --- populate input file tree ---
        root_block = self.tree.getBlockInfo("/")
        for block in root_block.children.values():
            if block.included:
                self.add_block(block)
            else:
                # add to unused blocks, sorted by name
                self._insort_by_name(
                    state.unused_blocks,
                    {
                        "name": block.name,
                        "path": block.path,
                    },
                )

        return True

    def write_file(self):
        # write input file tree to disk

        path = self._server.state.input_file
        print(f"Writing to {path}...")
        with open(path, "w") as f:
            f.write(self.tree.getInputFileString())

    def add_to_simput_model(self, type_info):
        simput_type = type_info.path
        params = type_info.orderedParameters()

        # add block parameters if type_info is actually a type
        if type_info.blockType() == type_info.name:
            params = params + type_info.parent.orderedParameters()

        params_dict = {}
        for param in params:
            if param.name != "type":  # type is handled outside simput
                params_dict[param.name] = self.format_simput_param(param)

        # sort params so that:
        #  - required params are first
        #  - everything else is alphabetical
        params_dict = dict(
            sorted(params_dict.items(), key=lambda kv: (not kv[1]["required"], kv[0]))
        )

        self.simput_types.append(simput_type)
        yaml_str = yaml.dump({simput_type: params_dict}, sort_keys=False)
        self.simput_manager.load_model(yaml_content=yaml_str)

    def get_type_info(self, block_info):
        type_info = block_info.getTypeBlock()
        if not type_info and len(block_info.types) > 0:
            # use first type as default
            default_type = list(block_info.types)[0]
            block_info.setBlockType(default_type)
            type_info = block_info.getTypeBlock()

        if not type_info:
            type_info = block_info

        return type_info

    def add_block(self, block_info):
        # Adds block and all children to vuetify block tree and simput
        state = self._server.state

        # --- create simput entry ---
        type_info = self.get_type_info(block_info)

        simput_type = type_info.path

        if simput_type not in self.simput_types:
            self.add_to_simput_model(type_info)

        proxy_id = block_info.path + "_type_" + simput_type
        self.pxm.create(simput_type, existing_obj=block_info, proxy_id=proxy_id)

        # --- add to vuetify tree ---
        block_entry = {
            "id": proxy_id,
            "name": block_info.name,
            "path": block_info.path,
            "children": [],
            "hidden_children": [],
        }

        if block_info.star:  # block can have new children
            star_node = block_info.star_node
            child_types = list(star_node.types.keys())
            if not child_types:
                child_types = [
                    block_info.name
                ]  # use block name if no child types exist
            block_entry["child_types"] = child_types

        # check if block is a child
        parent = block_info.parent
        if parent.path == "/":  # no parent
            # add block to tree sorted by name
            self._insort_by_name(state.block_tree, block_entry)
        else:
            parent_entry = self.get_block_tree_entry(parent.path)
            if block_info.included:
                parent_entry["children"].append(block_entry)
            else:
                parent_entry["hidden_children"].append(block_entry)

        # add children
        for child in block_info.children.values():
            self.add_block(child)

        state.dirty("block_tree")

    def get_block_tree_entry(self, path):
        # path is in form /ancestor_a/ancestor_b/.../parent/block
        # splitting by '/' gives ['', ancestor_a, ancestor_b, ... ,parent, block]
        ancestors = path.split("/")[1:]
        block_list = self._server.state.block_tree
        # find block in tree
        for ancestor in ancestors:
            for b in block_list:
                if b["name"] == ancestor:
                    block_list = b["children"]
                    parent_entry = b

        return parent_entry

    def remove_block(self, path):
        block_info = self.tree.getBlockInfo(path)
        parent_info = block_info.parent
        parent_info.removeChildBlock(block_info.name)

        state = self._server.state
        if parent_info.path == "/":
            for block_entry in state.block_tree:
                if block_entry["path"] == path:
                    break
            state.block_tree.remove(block_entry)
        else:
            parent_entry = self.get_block_tree_entry(parent_info.path)
            for block_entry in parent_entry["children"]:
                if block_entry["path"] == path:
                    break
            parent_entry["children"].remove(block_entry)

        # delete proxy
        proxy_id = path + "_type_" + self.get_type_info(block_info).path
        self.pxm.delete(proxy_id)

        state.dirty("block_tree")

    def add_child_block(self, parent_path, child_type):
        parent_info = self.tree.getBlockInfo(parent_path)
        new_name = parent_info.findFreeChildName()
        new_block = self.tree.addUserBlock(parent_path, new_name)
        new_block.included = True
        if child_type != parent_info.name:  # only set type if valid type was passed
            new_block.setBlockType(child_type)
        self.add_block(new_block)

    def include_child(self, parent_path, child_name):
        parent_info = self.tree.getBlockInfo(parent_path)
        child_info = parent_info.children[child_name]
        child_info.included = True

        parent_entry = self.get_block_tree_entry(parent_path)
        for child_entry in parent_entry["hidden_children"]:
            if child_entry["name"] == child_name:
                break
        parent_entry["hidden_children"].remove(child_entry)
        parent_entry["children"].append(child_entry)

        self._server.state.dirty("block_tree")
        self.update_editor()

    def format_simput_param(self, param):
        # formats a simput property from a ParameterInfo object for use in the simput model

        # strip vector wrapping from cpp type
        # TODO: handle matrices
        cpp_type = param.cpp_type
        cpp_type = cpp_type.split("std::vector<")[-1]
        cpp_type = cpp_type.split(">")[0]

        try:
            simput_type = self.cpp_type_map[cpp_type]
        except KeyError:
            # if the c++ type is not in the map, we assume it is a Moose object type and map it to string
            # simput_type = param.basic_type.split('Array:')[-1]
            simput_type = "string"

        param_entry = {
            "_label": param.name,
            "_help": param.toolTip(),
            "_tags": [param.group_name],
            "type": simput_type,
            "initial": param.getValue(),
            "required": param.required,
        }

        if param.options:
            if "domains" not in param_entry:
                param_entry["domains"] = []
            param_entry["domains"].append(
                {
                    "type": "LabelList",
                    "values": [{"text": val, "value": val} for val in param.options],
                }
            )

        if param.isVectorType():
            if "domains" not in param_entry:
                param_entry["domains"] = []
            param_entry["domains"].append(
                {"type": "UI", "properties": {"sizeControl": 1}}
            )

            # use indeterminate size for arrays
            # TODO: handle matrices
            param_entry["size"] = -1

        return param_entry

    def on_active_id(self, active_id, **kwargs):
        # this function triggers when a block is selected from the tree in the ui

        state = self._server.state

        if active_id is None:
            state.active_name = None
            state.active_type = None
            state.active_types = []
            return

        block_path = active_id.split("_type_")[0]
        active_block = self.tree.getBlockInfo(block_path)

        state.show_mesh = (
            active_block.name == "Mesh"
            or active_block.parent.name == "Mesh"
            or active_block.name == "BCs"
            or active_block.parent.name == "BCs"
        )

        if (
            active_block.parent.name == "BCs"
        ):  # boundary condition selected, highlight in mesh viewer
            state.bc_selected = True
            boundaries = active_block.paramValue("boundary")

            mapper = self.vtkMappers["blocks"]
            for block_id, info in state.blocks.items():
                mapper.SetBlockVisibility(info["index"], True)  # show all blocks
                mapper.SetBlockColor(info["index"], [1, 1, 1])  # make blocks white

            boundaries_info = {}
            mapper = self.vtkMappers["boundaries"]
            for boundary_id, info in state.boundaries.items():
                if boundary_id in boundaries:
                    idx = info["index"]
                    mapper.SetBlockVisibility(idx, True)  # show associated boundaries
                    red = [244, 67, 54]
                    mapper.SetBlockColor(
                        idx, list(map(lambda x: x / 255, red))
                    )  # set to default red color
                    boundaries_info[boundary_id] = {
                        "index": idx,
                        "visible": True,
                        "rgb": dict(zip("rgb", red)),
                        "html_color": "rgb" + str(tuple(red)),
                    }
                else:
                    self.vtkMappers["boundaries"].SetBlockVisibility(
                        info["index"], False
                    )  # hide others
            state.bc_boundaries = boundaries_info

            for nodeset, info in state.nodesets.items():
                self.vtkMappers["nodesets"].SetBlockVisibility(
                    info["index"], False
                )  # hide all nodesets

            self.vtkRenderWindow.Render()
            self._server.controller.update_input_mesh_view()
        else:
            if state.bc_selected:  # boundary de-selected
                state.bc_selected = False
                # reset viz to user selected values
                for set_type in ["blocks", "boundaries", "nodesets"]:
                    mapper = self.vtkMappers[set_type]
                    for set_id, info in state[set_type].items():
                        mapper.SetBlockVisibility(info["index"], info["visible"])
                        vtk_color = list(map(lambda x: x / 255, info["rgb"].values()))
                        mapper.SetBlockColor(info["index"], vtk_color)

                self.vtkRenderWindow.Render()
                self._server.controller.update_input_mesh_view()

        state.active_name = active_block.name
        state.name_editable = active_block.user_added
        state.active_types = list(active_block.types.keys())
        state.active_type = active_block.blockType()

    def on_active_type(self, active_type, old_type, **kwargs):
        state = self._server.state
        pxm = self.pxm

        block_path = state.active_id.split("_type_")[0]
        block_info = self.tree.getBlockInfo(block_path)

        type_info = block_info.types[active_type]
        simput_type = type_info.path

        if simput_type not in self.simput_types:
            self.add_to_simput_model(type_info)

        proxy_id = block_path + "_type_" + simput_type
        proxy = pxm.get(proxy_id)

        if proxy:
            # get existing proxy block info
            new_block_info = proxy._object
        else:
            # create block info of new type
            new_block_info = block_info.copy(block_info.parent)
            new_block_info.setBlockType(active_type)
            proxy = pxm.create(
                simput_type, existing_obj=new_block_info, proxy_id=proxy_id
            )

        # copy common parameters
        old_proxy_id = block_path + "_type_" + block_info.types[old_type].path
        old_proxy = pxm.get(old_proxy_id)
        new_props = proxy.list_property_names()
        for prop_name in old_proxy.list_property_names():
            if prop_name in new_props:
                old_val = old_proxy.get_property(prop_name)
                proxy.set_property(prop_name, old_val)
        self._server.controller.simput_reload_data()

        # insert new block into input file tree
        parent_info = block_info.parent
        parent_info.removeChildBlock(block_info.name)
        parent_info.addChildBlock(new_block_info)
        self.tree.path_map[block_path] = new_block_info

        state.active_id = proxy_id

    def on_active_name(self, active_name, **kwargs):
        state = self._server.state
        active_id = state.active_id

        path, simput_type = active_id.split("_type_")
        block_info = self.tree.getBlockInfo(path)
        parent_info = block_info.parent
        self.tree.renameUserBlock(parent_info.path, block_info.name, active_name)

        def update_paths_and_ids(block_entry, parent_info):
            old_path, simput_type = block_entry["id"].split("_type_")
            block_info = parent_info.children[block_entry["name"]]
            new_proxy_id = block_info.path + "_type_" + simput_type
            self.pxm.create(simput_type, existing_obj=block_info, proxy_id=new_proxy_id)
            self.pxm.delete(block_entry["id"])
            block_entry["path"] = block_info.path
            block_entry["id"] = new_proxy_id

            for child in block_entry["children"]:
                update_paths_and_ids(child, block_info)
            for child in block_entry["hidden_children"]:
                update_paths_and_ids(child, block_info)

            return new_proxy_id

        block_entry = self.get_block_tree_entry(path)
        block_entry["name"] = block_info.name
        state.active_id = update_paths_and_ids(block_entry, parent_info)
        state.active_ids = [state.active_id]
        state.dirty("block_tree")

    def toggle_mesh_viz(self, viz_type, viz_id):
        state = self._server.state

        info = state[viz_type][viz_id]
        info["visible"] = not info["visible"]
        state.dirty(viz_type)

        if viz_type == "bc_boundaries":
            viz_type = "boundaries"
        mapper = self.vtkMappers[viz_type]
        mapper.SetBlockVisibility(info["index"], info["visible"])
        self.vtkRenderWindow.Render()
        self._server.controller.update_input_mesh_view()

    def on_color_change(self, rgb_obj, viz_type, viz_id):
        state = self._server.state

        info = state[viz_type][viz_id]
        rgb = rgb_obj.values()
        info["html_color"] = "rgb" + str(tuple(rgb))
        info["rgb"] = rgb_obj
        state.dirty(viz_type)

        if viz_type == "bc_boundaries":
            viz_type = "boundaries"
        mapper = self.vtkMappers[viz_type]
        vtk_color = list(map(lambda x: x / 255, rgb))
        mapper.SetBlockColor(info["index"], vtk_color)
        self.vtkRenderWindow.Render()
        self._server.controller.update_input_mesh_view()

    def on_block_to_add(self, block_to_add, **kwargs):
        # this function triggers when a new block is added to the tree in the ui

        if block_to_add is None:
            return

        state = self._server.state

        # remove from unused_blocks
        for block_idx, block in enumerate(state.unused_blocks):
            if block["path"] == block_to_add:
                state.unused_blocks.pop(block_idx)

        # add to block tree
        block = self.tree.getBlockInfo(block_to_add)
        block.included = True
        self.add_block(block)
        state.block_to_add = None
        state.dirty("block_tree")

    def on_block_to_remove(self, block_to_remove, **kwargs):
        if block_to_remove is None:
            return

        self.remove_block(block_to_remove)
        self._server.state.block_to_remove = None

    def populate_from_editor(self, file_str):
        # repopulate entire tree
        # this is not optimal but it will work for now
        self.updating_from_editor = True
        old_mesh = self.tree.getBlockInfo("/Mesh")
        if self.set_input_file(file_str=file_str):
            state = self._server.state
            path, active_type_path = state.active_id.split("_type_")
            active_block = self.tree.getBlockInfo(path)
            if not active_block:
                # active block is not in new file tree
                # find most similar block and switch to it
                new_path = difflib.get_close_matches(path, self.tree.path_map.keys())[0]
                state.active_id = new_path + "_type_" + active_type_path
                state.active_ids = [state.active_id]
            else:
                # check if active type changed
                new_type_block = active_block.getTypeBlock()
                if (
                    new_type_block is not None
                    and new_type_block.name != state.active_type
                ):
                    state.active_type = new_type_block.name
                    state.active_id = path + "_type_" + new_type_block.path
                    state.active_ids = [state.active_id]

            # update vtk window if mesh changed
            new_mesh = self.tree.getBlockInfo("/Mesh")
            if old_mesh != new_mesh:
                self.update_render_window()
            self._server.controller.simput_reload_data()
        self.updating_from_editor = False

    def on_file_str(self, file_str):
        debounced_run(self.populate_from_editor, [file_str], delay=0.5)

    def toggle_mesh(self):
        state = self._server.state
        state.show_mesh = not state.show_mesh

    def get_ui(self):
        # return ui for input file editor

        ctrl = self._server.controller

        with vuetify.VCol(
            classes="fill-height flex-nowrap d-flex ma-0 pa-0",
            style="position: relative;",
        ) as input_ui:
            with html.Div(classes="fill-height d-flex flex-column"):
                with vuetify.VTreeview(
                    v_if=("block_tree.length > 0",),
                    items=("block_tree",),
                    style="width: 300px; flex: 1 1 0px; overflow: auto;",
                    hoverable=True,
                    rounded=True,
                    dense=True,
                    activatable=True,
                    active=("active_ids", ["/Mesh_type_/Mesh/FileMesh"]),
                    update_active="(active_ids) => {active_id = active_ids[0]}",
                ):
                    with vuetify.Template(v_slot_label="{ item }"):
                        with html.Div(
                            classes="d-flex justify-space-between align-center"
                        ):
                            html.P("{{item.name}}", classes="ma-0")

                            vuetify.VSpacer()

                            with vuetify.VMenu():
                                with vuetify.Template(
                                    v_slot_activator="{on, attrs}",
                                ):
                                    with vuetify.VBtn(
                                        v_if=(
                                            "item.child_types != undefined || item.hidden_children.length > 0",
                                        ),
                                        icon=True,
                                        v_on="on",
                                        v_bind="attrs",
                                        click="(event) => {event.stopPropagation(); event.preventDefault();}",
                                    ):
                                        vuetify.VIcon(
                                            "mdi-plus-circle",
                                        )

                                with vuetify.VList(
                                    style="overflow: auto; max-height: 90vh;"
                                ):
                                    vuetify.VListItem(
                                        "{{child.name}}",
                                        v_for="child in item.hidden_children",
                                        style="background: lightblue;",
                                        click=(
                                            self.include_child,
                                            "[item.path, child.name]",
                                        ),
                                    )
                                    vuetify.VListItem(
                                        "{{child_type}}",
                                        v_for="child_type in item.child_types",
                                        click=(
                                            self.add_child_block,
                                            "[item.path, child_type]",
                                        ),
                                    )

                            with vuetify.VBtn(
                                icon=True,
                                click="(event) => {event.stopPropagation(); event.preventDefault(); block_to_remove = item.path}",
                            ):
                                vuetify.VIcon("mdi-delete")

                with html.Div(style="width: 100%; padding: 10px;"):
                    with vuetify.VBtn(
                        v_if=("!add_block_open",),
                        click="add_block_open=true",
                        style="width: 100%;",
                    ):
                        vuetify.VIcon("mdi-plus-circle")

                    with vuetify.VBtn(
                        v_if=("add_block_open",),
                        click="add_block_open=false",
                        style="width: 100%;",
                    ):
                        vuetify.VIcon("mdi-close-circle")
                        html.P("Cancel", classes="ma-0")

                with vuetify.VCol(
                    v_if=("add_block_open",),
                    style="overflow-y: auto; flex: 1 1 0px; width: calc(100% - 20px);",
                    classes="d-flex flex-column",
                ):
                    with vuetify.VList():
                        vuetify.VListItem(
                            "{{block.name}}",
                            v_for="block in unused_blocks",
                            click="block_to_add = block.path; add_block_open = false;",
                        )

            with html.Div(
                style="position: relative; flex: 1 1 0px; height: 100%; display: flex; flex-direction: column; padding: 5px;",
            ):
                with html.Div(
                    style="position: absolute; top: 0px; width: 100%; display: flex; justify-content: center;",
                ):
                    with vuetify.VHover(
                        v_slot="{ hover }",
                        v_if=("!show_mesh",),
                    ):
                        with vuetify.VBtn(
                            click=self.toggle_mesh,
                            style="min-width: 50px; min-height: 0px; height: auto; padding: 2px; border-radius: 0px 0px 4px 4px; z-index: 3;",
                        ):
                            with html.Div(
                                style="display: flex; flex-direction: column;"
                            ):
                                vuetify.VIcon("mdi-chevron-down", style="height: 15px;")
                                with vuetify.VSlideYTransition():
                                    vuetify.VIcon(
                                        "mdi-cube-outline",
                                        v_if="hover",
                                        style="padding-top: 15px;",
                                    )

                with html.Div(
                    v_if=("show_mesh",),
                    style="position: relative; width: 100%; height: 50vh; border-radius: 5px; overflow: hidden; margin-bottom: 10px;",
                ):
                    with html.Div(
                        style="position: absolute; bottom: 0px; width: 100%; display: flex; justify-content: center;"
                    ):
                        with vuetify.VHover(
                            v_slot="{ hover }",
                        ):
                            with vuetify.VBtn(
                                click=self.toggle_mesh,
                                style="min-width: 50px; min-height: 0px; height: auto; padding: 2px; border-radius: 4px 4px 0px 0px; z-index: 3;",
                            ):
                                with html.Div(
                                    style="display: flex; flex-direction: column;"
                                ):
                                    with vuetify.VSlideYReverseTransition():
                                        vuetify.VIcon(
                                            "mdi-cube-off-outline",
                                            v_if="hover",
                                            style="padding-bottom: 5px;",
                                        )
                                    vuetify.VIcon(
                                        "mdi-chevron-up", style="height: 15px;"
                                    )

                    renderWindow = self.update_render_window()
                    if USE_PARAVIEW:
                        renderView = paraview.VtkRemoteView(
                            renderWindow, interactive_ratio=1, ref="input_view"
                        )
                    else:
                        renderView = vtk.VtkRemoteView(
                            renderWindow, interactive_ratio=1, ref="input_view"
                        )
                    ctrl.update_input_mesh_view = renderView.update

                    # block, boundary, nodeset selector
                    with html.Div(
                        style="position: absolute; bottom: 0px; left: 0px; display: flex; z-index: 1;",
                    ):

                        def create_viz_editor(label, array_name, is_bc=False):
                            if is_bc:
                                cond1 = ("bc_selected", False)
                                cond2 = None

                            else:
                                cond1 = ("!bc_selected",)
                                cond2 = ("show_" + array_name, False)

                            with html.Div(
                                style="position: relative; display: flex; align-items: flex-end; justify-content: center; width: 150px;",
                                v_show=cond1,
                            ):
                                if not is_bc:
                                    # toggle display button
                                    with html.Div(
                                        style="position: absolute; width: 100%; display: flex; justify-content: center;",
                                    ):
                                        with vuetify.VHover(
                                            v_slot="{ hover }",
                                        ):
                                            with vuetify.VBtn(
                                                small=True,
                                                depressed=True,
                                                click="show_" + array_name + " = true",
                                                style="border-radius: 4px 4px 0px 0px; height: auto; min-height: 0px; width: 80%;",
                                                v_show="!show_" + array_name,
                                            ):
                                                with html.Div(
                                                    style="display: flex; flex-direction: column;"
                                                ):
                                                    with vuetify.VSlideYReverseTransition():
                                                        vuetify.VIcon(
                                                            "mdi-chevron-up",
                                                            v_if="hover",
                                                            style="height: 15px; padding: 5px;",
                                                        )
                                                    html.P(
                                                        label,
                                                        style="margin: 0; padding: 5px;",
                                                    )

                                # viz and color selectors
                                with vuetify.VSlideYReverseTransition():
                                    with vuetify.VCard(
                                        v_if=cond2,
                                        style="display: flex; flex-direction: column; position: relative;",
                                    ):
                                        with vuetify.VCardTitle(style="padding: 10px;"):
                                            if is_bc:
                                                html.P(
                                                    label,
                                                    style="margin: 0; text-align: center; word-break: normal; font-size: 14px;",
                                                )
                                            else:
                                                with html.Div(
                                                    style="position: absolute; left: 0; top: 10px; width: 100%; display: flex; justify-content: center; z-index: 1;"
                                                ):
                                                    with vuetify.VHover(
                                                        v_slot="{ hover }",
                                                    ):
                                                        with vuetify.VBtn(
                                                            text=("!hover",),
                                                            small=True,
                                                            click="show_"
                                                            + array_name
                                                            + " = false",
                                                            style="min-height: 0px; height: auto;",
                                                        ):
                                                            with html.Div(
                                                                style="display: flex; flex-direction: column;"
                                                            ):
                                                                html.P(
                                                                    label,
                                                                    style="margin: 0;",
                                                                )
                                                                with vuetify.VSlideYTransition():
                                                                    vuetify.VIcon(
                                                                        "mdi-chevron-down",
                                                                        v_if="hover",
                                                                        style="height: 15px; padding-top: 15px; padding-bottom: 10px;",
                                                                    )
                                        with vuetify.VCardText(style="padding: 5px;"):
                                            with html.Div(
                                                style="position: relative; display: flex; align-items: center; justify-content: space-between;",
                                                v_for=(
                                                    "(value, key) in " + array_name,
                                                ),
                                            ):
                                                with vuetify.VBtn(
                                                    icon=True,
                                                    click=(
                                                        self.toggle_mesh_viz,
                                                        "['" + array_name + "', key]",
                                                    ),
                                                ):
                                                    vuetify.VIcon(
                                                        "mdi-eye-outline",
                                                        v_if="value.visible",
                                                    )
                                                    vuetify.VIcon(
                                                        "mdi-eye-off-outline",
                                                        v_if="!value.visible",
                                                    )

                                                html.P("{{key}}", style="margin: 0;")

                                                with vuetify.VMenu(
                                                    top=True,
                                                    offset_x=10,
                                                    offset_y=10,
                                                    close_on_content_click=False,
                                                ):
                                                    with vuetify.Template(
                                                        v_slot_activator="{ on }",
                                                    ):
                                                        with vuetify.VBtn(
                                                            icon=True,
                                                            v_on="on",
                                                        ):
                                                            html.Div(
                                                                style=(
                                                                    "{width: '15px', height: '15px', background: value.html_color, border: '1px solid black'}",
                                                                ),
                                                            )
                                                    vuetify.VColorPicker(
                                                        hide_canvas=True,
                                                        hide_sliders=True,
                                                        hide_inputs=True,
                                                        hide_mode_switch=True,
                                                        show_swatches=True,
                                                        v_model=("value.rgb",),
                                                        input=(
                                                            self.on_color_change,
                                                            "[$event, '"
                                                            + array_name
                                                            + "', key]",
                                                        ),
                                                    )

                        create_viz_editor(
                            "Blocks",
                            "blocks",
                        )
                        create_viz_editor("Boundaries", "boundaries")
                        create_viz_editor("Nodesets", "nodesets")
                        create_viz_editor(
                            "Associated Boundaries", "bc_boundaries", True
                        )

                    html.Div(
                        style="position: absolute; height: 100%; width: 100%; top: 0px; left: 0px; backdrop-filter: blur(5px); z-index: 2;",
                        v_show=("mesh_invalid", False),
                    )

                with vuetify.VCard(style="width: 100%; flex-grow: 1;"):
                    with vuetify.VCardTitle():
                        vuetify.VTextField(
                            v_model=("active_name"),
                            v_if=("active_name != null",),
                            disabled=("!name_editable",),
                            label="Name",
                            dense=True,
                            hide_details=True,
                            change=(self.on_active_name, "[$event]"),
                        )
                        vuetify.VSpacer()
                        vuetify.VCombobox(
                            v_model=("active_type",),
                            v_if=("active_type != null",),
                            items=("active_types",),
                            label="Type",
                            dense=True,
                            hide_details=True,
                            change=(self.on_active_type, "[$event, active_type]"),
                        )
                    vuetify.VDivider()
                    with vuetify.VCardText(
                        style=(
                            "{height: show_mesh ? 'calc(50vh - 140px)' : 'calc(100vh - 140px)'}",
                        ),
                        classes="pa-0",
                    ):
                        simput.SimputItem(
                            item_id=("active_id",),
                            style="overflow: auto; height: 100%;",
                            classes="px-2 py-3",
                        )

            with vuetify.VHover(
                v_slot="{ hover }",
                style="position: absolute; top: 10px; right: 0px; z-index: 3;",
                v_if=("!show_file_editor",),
            ):
                with vuetify.VBtn(
                    click=self.toggle_editor,
                    style="min-width: 0px; min-height: 50px; padding: 2px; border-radius: 4px 0px 0px 4px;",
                ):
                    with vuetify.VSlideXReverseTransition():
                        vuetify.VIcon(
                            "mdi-file-document-edit-outline",
                            v_if="hover",
                            style="padding-right: 5px;",
                        )
                    vuetify.VIcon(
                        "mdi-chevron-left",
                        style="width: 15px;",
                    )

            with vuetify.VSlideXReverseTransition():
                with html.Div(
                    v_show=("show_file_editor", False),
                    style="flex: 1 1 0px; height: 100%; position: relative;",
                ):
                    with vuetify.VHover(
                        v_slot="{ hover }",
                        style="position: absolute; top: 10px; left: 0; z-index: 3;",
                    ):
                        with vuetify.VBtn(
                            click=self.toggle_editor,
                            style="min-width: 0px; min-height: 50px; padding: 2px; background: gray; border-radius: 0px 4px 4px 0px;",
                        ):
                            vuetify.VIcon(
                                "mdi-chevron-right",
                                color="white",
                                style="width: 15px;",
                            )
                            with vuetify.VSlideXTransition():
                                vuetify.VIcon(
                                    "mdi-arrow-collapse-right",
                                    v_if="hover",
                                    color="white",
                                    style="padding-left: 10px;",
                                )

                    peacock.Editor(
                        contents=("file_str", ""),
                        filepath=("input_file", ""),
                        change=(self.on_file_str, "[$event]"),
                    )

        return input_ui

    def update_render_window(self):
        server = self._server
        state, ctrl = server.state, server.controller
        input_file = state.input_file
        exe_path = state.executable

        # save temp input file to run executable with
        tmp_input_file = f"{os.path.splitext(input_file)[0]}_tmp.i"
        with open(tmp_input_file, "w+") as f:
            f.write(self.tree.getInputFileString())

        # run executable to get mesh
        tmp_mesh_file = f"{os.path.splitext(input_file)[0]}_tmp_mesh.e"
        try:
            ExeLauncher.runExe(
                exe_path, ["-i", tmp_input_file, "--mesh-only", tmp_mesh_file]
            )
        except BadExecutableException:
            print("'--mesh-only' executable run failed")
            state.mesh_invalid = True
            state.flush()
            return

        reader = vtkExodusIIReader()
        reader.SetFileName(tmp_mesh_file)
        reader.Update()

        # indices of exodus object types in the output multi-block
        exodus_mb_type_order = [
            vtkExodusIIReader.ELEM_BLOCK,  # 0
            vtkExodusIIReader.FACE_BLOCK,  # 1
            vtkExodusIIReader.EDGE_BLOCK,  # 2
            vtkExodusIIReader.ELEM_SET,  # 3
            vtkExodusIIReader.SIDE_SET,  # 4
            vtkExodusIIReader.FACE_SET,  # 5
            vtkExodusIIReader.EDGE_SET,  # 6
            vtkExodusIIReader.NODE_SET,  # 7
        ]

        block_type = vtkExodusIIReader.ELEM_BLOCK
        boundary_type = vtkExodusIIReader.SIDE_SET
        nodeset_type = vtkExodusIIReader.NODE_SET

        # traverse exodus multi-block
        blocks = []
        block_idxs = []
        boundaries = []
        boundary_idxs = []
        nodesets = []
        nodeset_idxs = []
        index = 0
        for obj_type in exodus_mb_type_order:
            index += 1
            for j in range(reader.GetNumberOfObjects(obj_type)):
                index += 1
                name = reader.GetObjectName(obj_type, j)
                if name.startswith("Unnamed"):
                    name = reader.GetObjectId(obj_type, j)
                reader.SetObjectStatus(obj_type, j, 1)  # load for rendering
                if obj_type == block_type:
                    blocks.append(name)
                    block_idxs.append(index)
                elif obj_type == boundary_type:
                    boundaries.append(name)
                    boundary_idxs.append(index)
                elif obj_type == nodeset_type:
                    nodesets.append(name)
                    nodeset_idxs.append(index)

        def create_vtk_pipeline(set_list, mb_idxs, visible, rgb):
            # extracts group of blocks from exodus tree and creates rendering pipeline
            extractor = vtkExtractBlock()
            extractor.SetInputConnection(reader.GetOutputPort())
            for idx in mb_idxs:
                extractor.AddIndex(idx)
            geometry = vtkDataSetSurfaceFilter()
            geometry.SetInputConnection(extractor.GetOutputPort())
            mapper = vtkCompositePolyDataMapper()
            mapper.SetInputConnection(geometry.GetOutputPort())
            cdsa = vtkCompositeDataDisplayAttributes()
            mapper.SetCompositeDataDisplayAttributes(cdsa)
            actor = vtkActor()
            actor.SetMapper(mapper)
            mapper.Update()

            # store info in dictionary
            info = {}
            for idx, set_id in enumerate(set_list):
                info[str(set_id)] = {
                    "visible": visible,
                    "rgb": dict(zip("rgb", rgb)),
                    "html_color": "rgb" + str(tuple(rgb)),
                    "index": idx + 1,
                }

                mapper.SetBlockVisibility(idx + 1, visible)
                vtk_color = list(map(lambda x: x / 255, rgb))
                mapper.SetBlockColor(idx + 1, vtk_color)

            return actor, mapper, info

        block_actor, block_mapper, block_info = create_vtk_pipeline(
            blocks, block_idxs, True, [255, 255, 255]
        )
        boundary_actor, boundary_mapper, boundary_info = create_vtk_pipeline(
            boundaries, boundary_idxs, False, [244, 67, 54]
        )
        nodeset_actor, nodeset_mapper, nodeset_info = create_vtk_pipeline(
            nodesets, nodeset_idxs, False, [244, 67, 54]
        )

        block_actor.GetProperty().SetRepresentationToWireframe()
        boundary_actor.GetProperty().SetRepresentationToSurface()
        nodeset_actor.GetProperty().SetRepresentationToPoints()
        nodeset_actor.GetProperty().SetPointSize(5)

        renderer = vtkRenderer()
        renderer.SetBackground(0.5, 0.5, 0.5)
        renderer.SetBackground2(0.75, 0.75, 0.75)
        renderer.SetGradientBackground(True)
        renderer.AddActor(block_actor)
        renderer.AddActor(boundary_actor)
        renderer.AddActor(nodeset_actor)

        if self.vtkRenderWindow is None:
            # no mesh rendered yet
            if USE_PARAVIEW:
                view = simple.CreateView("RenderView")
                view.OrientationAxesVisibility = 0
                renderWindow = view.GetRenderWindow()
            else:
                renderWindow = vtkRenderWindow()
            renderWindow.SetOffScreenRendering(1)
            interactor = vtkRenderWindowInteractor()
            interactor.SetRenderWindow(renderWindow)
            interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
            renderWindow.AddRenderer(renderer)
            renderWindow.Render()
            self.vtkRenderWindow = renderWindow
        else:
            # mesh rendered already
            renderWindow = self.vtkRenderWindow
            renderWindow.RemoveRenderer(self.vtkRenderer)
            renderWindow.AddRenderer(renderer)
            renderWindow.Render()
            ctrl.update_input_mesh_view()

        self.vtkMappers = {
            "blocks": block_mapper,
            "boundaries": boundary_mapper,
            "nodesets": nodeset_mapper,
        }
        self.vtkRenderer = renderer

        state.blocks = block_info
        state.boundaries = boundary_info
        state.nodesets = nodeset_info
        state.mesh_invalid = False
        state.flush()

        return view if USE_PARAVIEW else renderWindow

    def _insort_by_name(self, dict_list, entry):
        # adds dictionary to list of dictionaries, sorted by 'name' key
        if len(dict_list) == 0:
            dict_list[:] = [entry]
            return

        for idx, d in enumerate(dict_list):
            if entry["name"] < d["name"]:
                dict_list.insert(idx, entry)
                return

        dict_list.append(entry)


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
