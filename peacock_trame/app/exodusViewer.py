import os

import numpy as np
from trame.widgets import html, paraview, vuetify

from .core.common.utils import throttled_run
from .core.exodusViewer.time_step import TimeStepController

try:
    from paraview import simple

    PARAVIEW_INSTALLED = True
except ModuleNotFoundError:
    PARAVIEW_INSTALLED = False


CHECKER_BACKGROUND = "url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAGElEQVQYlWNgYGCQwoKxgqGgcJA5h3yFAAs8BRWVSwooAAAAAElFTkSuQmCC) repeat"


class ExodusViewer:
    def __init__(self, server):
        if not PARAVIEW_INSTALLED:
            return

        self._server = server
        self.state = server.state
        self.ctrl = server.controller

        state = server.state
        input_file = state.input_file
        state.ex2_file = os.path.splitext(input_file)[0] + "_out.e"
        state.ex2_exists = False
        state.contour_levels = []

        self.render_view = None
        self.clip = None
        self.contour = None

        self.time_ctrl = TimeStepController(server)

    def get_ui(self):
        if not PARAVIEW_INSTALLED:
            # This page cannot work with VTK alone, for now
            with html.Div(
                style="""
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    width: 100%;
                    height: 100%;
                """,
            ) as container:
                html.H1("This page requires ParaView.")
                html.A(
                    "https://github.com/kitware/peacock#running-the-software",
                    href="https://github.com/kitware/peacock#running-the-software",
                    target="_blank",
                )

            return container

        with vuetify.VCol(
            classes="fill-height ma-0 pa-0 d-flex",
        ) as container:
            with html.Div(
                style="width: 30%; padding: 10px;",
            ):
                with html.Div(
                    style="display: flex; align-items: center; justify-content: space-between;"
                ):
                    html.H3(os.path.split(self.state.ex2_file)[1])
                    vuetify.VAlert(
                        "File does not exists.",
                        v_if=("!ex2_exists",),
                        type="error",
                        dense=True,
                        classes="ma-0",
                    )

                vuetify.VSelect(
                    v_model=("active_rep_type", "Surface"),
                    label="Representation",
                    items=(["Surface", "Surface With Edges", "Wireframe", "Points"],),
                    change=(self.on_active_rep_type, "[$event]"),
                )

                vuetify.VSwitch(
                    v_model=("show_axes", False),
                    label="Show Axes",
                    change=(self.toggle_axes, "[$event]"),
                )

                vuetify.VSelect(
                    v_model=("active_variable", None),
                    label="Variable",
                    items=("variables", []),
                    change=(self.on_active_variable, "[$event]"),
                    clearable=True,
                )

                vuetify.VSwitch(
                    v_model=("show_clip", False),
                    label="Clip",
                    change=(self.toggle_clip, "[$event]"),
                )

                with html.Div(style="display: flex;"):
                    vuetify.VSelect(
                        v_model=("clip_direction", "X"),
                        items=(["X", "Y", "Z"],),
                        change=(self.on_clip_direction, "[$event]"),
                        style="padding: 0; margin: 0; flex-grow: 0; width: 50px;",
                    )

                    vuetify.VSlider(
                        v_model=("clip_origin", 0),
                        min=("clip_min", 0),
                        max=("clip_max", 0),
                        thumb_label="always",
                        step="0.001",
                        input=(self.on_clip_origin, "[$event]"),
                    )

                    with vuetify.VBtn(
                        click=self.flip_clip,
                        icon=True,
                    ):
                        vuetify.VIcon("mdi-flip-horizontal")

                vuetify.VSwitch(
                    v_model=("show_contours", False),
                    label="Contours",
                    change=(self.toggle_contours, "[$event]"),
                )

                with html.Div(
                    style="display: flex; justify-content: space-between;",
                ):
                    vuetify.VTextField(
                        label="Count",
                        type="number",
                        v_model=("num_contours", 3),
                        rules=("[value => value >= 0 || 'Must be >= 0']",),
                        change=(self.on_num_contours, "[$event]"),
                        style="flex-grow: 0; width: 50px; margin: 0; padding: 0;",
                    )

                    vuetify.VSwitch(
                        v_model=("auto_gen_contours", True),
                        label="Auto Divide",
                        change=(self.on_auto_gen_contours, "[$event]"),
                        style="margin: 0; padding: 0;",
                    )

                    with vuetify.VBtn(
                        click=(self.spread_contour_levels, "[num_contours]"),
                        icon=True,
                        disabled=("auto_gen_contours",),
                    ):
                        vuetify.VIcon("mdi-arrow-expand-vertical")

                with html.Div(style="overflow: auto; max-height: 300px;"):
                    vuetify.VTextField(
                        v_for="idx in contour_levels.length",
                        v_model="contour_levels[idx - 1]",
                        change=(self.on_contour_level, "[idx - 1, $event]"),
                        label=("idx",),
                        disabled=("auto_gen_contours",),
                    )

            with html.Div(
                style="flex-grow: 1; position: relative;",
            ):
                renderView = paraview.VtkRemoteView(
                    self.update_render_window(), interactive_ratio=1, ref="exodus_view"
                )
                self.ctrl.update_exodus_view = renderView.update

                # ex2 timestep controller
                with html.Div(
                    style="position: absolute; top: 0px; left: 0px; display: flex; z-index: 1;",
                ):
                    self.time_ctrl.get_ui()

                # block, boundary, nodeset selector
                with html.Div(
                    style="position: absolute; bottom: 0px; left: 0px; display: flex; z-index: 1;",
                ):

                    def create_viz_editor(label, array_name):
                        with html.Div(
                            style="position: relative; display: flex; align-items: flex-end; justify-content: center; width: 150px;",
                        ):
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
                                    v_if=("show_" + array_name, False),
                                    style="display: flex; flex-direction: column; position: relative;",
                                ):
                                    with vuetify.VCardTitle():
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
                                            v_for=("(value, key) in " + array_name,),
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
                                                                "{width: '15px', height: '15px', border: '1px solid black', background: value.html_color}",
                                                            ),
                                                        )
                                                vuetify.VColorPicker(
                                                    hide_canvas=True,
                                                    hide_sliders=True,
                                                    hide_inputs=True,
                                                    hide_mode_switch=True,
                                                    show_swatches=True,
                                                    v_model=("value.rgba",),
                                                    input=(
                                                        self.on_color_change,
                                                        "[$event, '"
                                                        + array_name
                                                        + "', key]",
                                                    ),
                                                )

                    create_viz_editor(
                        "Blocks",
                        "ex2_blocks",
                    )
                    create_viz_editor("Boundaries", "ex2_boundaries")
                    create_viz_editor("Nodesets", "ex2_nodesets")

        return container

    def on_active_rep_type(self, rep_type):
        self.active_rep.Representation = rep_type
        self.ctrl.update_exodus_view()

    def toggle_axes(self, show):
        self.active_view.AxesGrid.Visibility = show
        self.ctrl.update_exodus_view()

    def toggle_mesh_viz(self, viz_type, viz_id):
        state = self.state

        info = state[viz_type][viz_id]
        info["visible"] = not info["visible"]
        state.dirty(viz_type)

        entry = "/Root/" + viz_id
        block_selectors = self.active_rep.BlockSelectors.GetData()
        if entry in block_selectors:
            block_selectors.remove(entry)
        else:
            block_selectors.append(entry)
        self.active_rep.BlockSelectors = block_selectors

        self.ctrl.update_exodus_view()

    def on_color_change(self, rgba_obj, viz_type, viz_id):
        state = self.state

        info = state[viz_type][viz_id]
        rgba = list(rgba_obj.values())
        info["rgba"] = rgba_obj

        block_colors = self.active_rep.BlockColors.GetData()
        block_path = "/Root/" + viz_id
        if block_path in block_colors:
            idx = block_colors.index(block_path)
            del block_colors[idx : (idx + 4)]  # remove path + rgb values

        if rgba == [0, 0, 0, 0]:  # transparent
            info["html_color"] = CHECKER_BACKGROUND
        else:
            info["html_color"] = "rgba" + str(tuple(rgba))
            vtk_color = list(map(lambda x: str(x / 255), rgba[0:3]))

            block_colors.append(block_path)
            for color in vtk_color:
                block_colors.append(color)

        state.dirty(viz_type)
        self.active_rep.BlockColors = block_colors
        self.ctrl.update_exodus_view()

    def check_file(self):
        if not PARAVIEW_INSTALLED:
            return False

        state = self.state
        if state.ex2_exists:
            return

        ex2_file = state.ex2_file
        if os.path.exists(ex2_file):
            state.ex2_exists = True
            self.update_render_window()

    def on_active_variable(self, var):
        simple.ColorBy(self.active_rep, ("POINTS", var))
        simple.HideScalarBarIfNotNeeded(self.active_lut, self.render_view)
        if var is not None:
            self.active_rep.SetScalarBarVisibility(self.render_view, True)
            lut = simple.GetColorTransferFunction(var)
            lut.RescaleTransferFunction(*self.data_ranges[var])
            self.active_lut = lut
            if self.contour:
                self.contour.ContourBy = ["POINTS", var]
                if self.state.auto_gen_contours:
                    self.state.active_variable = var
                    self.spread_contour_levels(self.state.num_contours)
        self.ctrl.update_exodus_view()

    def _add_source(self, source):
        simple.Hide(self.active_source, self.render_view)
        source.Input = self.active_source
        rep = simple.Show(source, self.render_view)
        rep.BlockSelectors = self.active_rep.BlockSelectors
        rep.BlockColors = self.active_rep.BlockColors
        rep.Representation = self.active_rep.Representation

        active_var = self.state.active_variable
        simple.ColorBy(rep, ("POINTS", active_var))
        simple.HideScalarBarIfNotNeeded(self.active_lut, self.render_view)
        rep.SetScalarBarVisibility(self.render_view, True)
        self.active_lut.RescaleTransferFunction(*self.data_ranges[active_var])

        self.active_source = source
        self.active_rep = rep

    def _remove_source(self, source):
        simple.Hide(source, self.render_view)

        sources = list(simple.GetSources().values())
        for s in sources:
            if hasattr(s, "Input") and s.Input == source:
                s.Input = source.Input
                break

        if self.active_source == source:  # active source is  changing
            rep = simple.Show(source.Input, self.render_view)
            rep.BlockSelectors = self.active_rep.BlockSelectors
            rep.BlockColors = self.active_rep.BlockColors
            rep.Representation = self.active_rep.Representation

            active_var = self.state.active_variable
            simple.ColorBy(rep, ("POINTS", active_var))
            simple.HideScalarBarIfNotNeeded(self.active_lut, self.render_view)
            rep.SetScalarBarVisibility(self.render_view, True)
            self.active_lut.RescaleTransferFunction(*self.data_ranges[active_var])

            self.active_source = source.Input
            self.active_rep = rep

    def toggle_clip(self, show):
        if self.clip is None:
            self.clip = simple.Clip(Input=self.ex2)

        if show:
            self._add_source(self.clip)
        else:
            self._remove_source(self.clip)

        # self.clip.UpdatePipeline()
        self.ctrl.update_exodus_view()

    def on_clip_direction(self, direction):
        if self.clip is None:
            return

        idx = ["X", "Y", "Z"].index(direction)
        normal = [0.0, 0.0, 0.0]
        normal[idx] = 1.0
        self.clip.ClipType.Normal = normal

        clip_min, clip_max = self.bounds[(idx * 2) : (idx * 2 + 2)]
        self.state.clip_min = clip_min
        self.state.clip_max = clip_max
        self.state.clip_origin = clip_min + (clip_max - clip_min) / 2

        self.ctrl.update_exodus_view()

    def on_clip_origin(self, axis_origin):
        if self.clip is None:
            return

        throttled_run(self._move_clip, [axis_origin], 10)

    def flip_clip(self):
        if self.clip is None:
            return

        self.clip.Invert = not self.clip.Invert
        self.ctrl.update_exodus_view()

    def _move_clip(self, axis_origin):
        origin = self.clip.ClipType.Origin
        idx = ["X", "Y", "Z"].index(self.state.clip_direction)
        origin[idx] = axis_origin
        self.clip.ClipType.Origin = origin

        self.ctrl.update_exodus_view()

    def toggle_contours(self, show):
        if self.contour is None:
            self.contour = simple.Contour(Input=self.ex2)

        if show:
            self.contour.ContourBy = ["POINTS", self.state.active_variable]
            self.contour.Isosurfaces = self.state.contour_levels
            self._add_source(self.contour)
        else:
            self._remove_source(self.contour)

        self.ctrl.update_exodus_view()

    def spread_contour_levels(self, num_contours):
        var_min, var_max = self.data_ranges[self.state.active_variable]
        levels = list(np.linspace(var_min, var_max, int(num_contours)))
        self.state.contour_levels = levels
        self.state.dirty("contour_levels")

        if self.contour:
            self.contour.Isosurfaces = levels
            self.ctrl.update_exodus_view()

    def on_auto_gen_contours(self, auto_gen):
        if auto_gen:
            self.spread_contour_levels(self.state.num_contours)

    def on_num_contours(self, num_contours):
        if num_contours == "":
            return

        num_contours = int(num_contours)

        if self.state.auto_gen_contours:
            self.spread_contour_levels(num_contours)
        else:
            levels = self.state.contour_levels
            if len(levels) > num_contours:
                levels = levels[0:num_contours]
            else:
                levels = levels + [levels[-1]] * (num_contours - len(levels))

            self.state.contour_levels = levels

            if self.contour:
                self.contour.Isosurfaces = levels
                self.ctrl.update_exodus_view()

    def on_contour_level(self, idx, level):
        self.state.contour_levels[idx] = float(level)
        self.state.dirty("contour_levels")

        if self.contour:
            self.contour.Isosurfaces = self.state.contour_levels
            self.ctrl.update_exodus_view()

    def add_contour_level(self):
        state = self.state
        state.contour_levels.append(state.contour_levels[-1])
        state.num_contours += 1
        state.dirty("contour_levels")

    def update_render_window(self):
        state = self.state

        if self.render_view is None:
            view = simple.CreateView("RenderView")
            view.OrientationAxesVisibility = 0
            simple.SetActiveView(view)

            color_palette = simple.GetSettingsProxy("ColorPalette")
            color_palette.BackgroundColorMode = "Gradient"
            color_palette.Background = [0.5, 0.5, 0.5]
            color_palette.Background2 = [0.75, 0.75, 0.75]

            renderWindow = view.GetRenderWindow()
            renderWindow.SetOffScreenRendering(1)

            self.render_view = view

        view = self.render_view

        if state.ex2_exists:
            ex2 = simple.IOSSReader(FileName=state.ex2_file)
            ex2.NodeBlockFields.SelectAll()
            variables = ex2.NodeBlockFields.GetData()
            active_var = variables[0]
            rep = simple.Show(ex2, view)
            simple.ColorBy(rep, ("POINTS", active_var))
            rep.SetScalarBarVisibility(view, True)

            view.ResetCamera()

            block_selectors = []

            def create_mesh_info(set_list, visible):
                # store info in dictionary
                info = {}
                for set_id in set_list:
                    info[str(set_id)] = {
                        "visible": visible,
                        "rgba": {"r": 0, "g": 0, "b": 0, "a": 0},
                        "html_color": CHECKER_BACKGROUND,
                    }

                    if visible:
                        block_selectors.append("/Root/" + set_id)

                return info

            ex2.ElementBlocks.SelectAll()
            ex2.SideSets.SelectAll()
            ex2.NodeSets.SelectAll()
            state.ex2_blocks = create_mesh_info(ex2.ElementBlocks, True)
            state.ex2_boundaries = create_mesh_info(ex2.SideSets, False)
            state.ex2_nodesets = create_mesh_info(ex2.NodeSets, False)

            rep.BlockSelectors = block_selectors

            # compute data ranges
            data = ex2.GetPointDataInformation()
            data_ranges = {}
            for idx in range(data.GetNumberOfArrays()):
                a = data.GetArray(idx)
                if a.Name in variables:
                    data_ranges[a.Name] = a.GetRange()

            lut = simple.GetColorTransferFunction(active_var)
            lut.RescaleTransferFunction(data_ranges[active_var])

            bounds = ex2.GetDataInformation().GetBounds()
            clip_min, clip_max = bounds[0:2]
            state.clip_min = clip_min
            state.clip_max = clip_max
            state.clip_origin = clip_min + (clip_max - clip_min) / 2
            state.variables = variables
            state.active_variable = active_var

            self.data_ranges = data_ranges
            self.bounds = bounds
            self.ex2 = ex2
            self.active_source = ex2
            self.active_lut = lut
            self.active_rep = rep
            self.active_lut = lut
            self.active_view = view

            # time step controller
            self.time_ctrl.set_ex2(ex2)
            self.time_ctrl.set_render_function(self.ctrl.update_exodus_view)

            self.spread_contour_levels(state.num_contours)

        return view
