from trame.app import asynchronous
from trame.widgets import html, vuetify

try:
    from paraview import simple
except ModuleNotFoundError:
    # The Exodus Viewer is disabled when ParaView is not installed
    # So, no extra handling is needed in this file
    # But, this file is still imported, so this try/catch is required
    pass

import asyncio


class TimeStepController:
    _next_id = 0

    def __init__(self, server):
        # give each instantiation a unique id
        self._id = TimeStepController._next_id
        TimeStepController._next_id += 1

        self.frame_step_time = 0.5  # time between frames in seconds

        self._server = server
        self._state = server.state

        self._ex2 = None
        self._playing = False

        self._set_state_var("playing", False)
        self._set_state_var("curr_frame", 1)
        self._set_state_var("num_frames", 1)

    def set_ex2(self, ex2):
        animation_scene = simple.GetAnimationScene()
        animation_scene.GoToFirst()
        self._curr_frame = 1
        self._num_frames = animation_scene.NumberOfFrames
        self._set_state_var("curr_frame", 1)
        self._set_state_var("num_frames", animation_scene.NumberOfFrames)
        self._animation_scene = animation_scene

    def set_render_function(self, func):
        self._render_function = func

    def get_ui(self):
        with html.Div(style="display: flex; flex-direction: column;") as container:
            with html.Div(style="display: flex; justify-content: center;"):
                html.P(
                    f"{{{{ {self._get_state_var_name('curr_frame')} }}}} / {{{{ {self._get_state_var_name('num_frames')} }}}}",
                    classes="ma-0",
                )
            with html.Div(style="display: flex;"):
                # first frame btn
                with vuetify.VBtn(
                    click=self._first,
                    icon=True,
                ):
                    vuetify.VIcon("mdi-step-backward-2")

                # prev frame btn
                with vuetify.VBtn(
                    click=self._prev,
                    icon=True,
                ):
                    vuetify.VIcon("mdi-step-backward")

                # play btn
                with vuetify.VBtn(
                    click=self._play,
                    icon=True,
                    v_if=f"!{self._get_state_var_name('playing')}",
                ):
                    vuetify.VIcon("mdi-play")

                # pause btn
                with vuetify.VBtn(
                    click=self._stop,
                    icon=True,
                    v_if=self._get_state_var_name("playing"),
                ):
                    vuetify.VIcon("mdi-pause")

                # next frame btn
                with vuetify.VBtn(
                    click=self._next,
                    icon=True,
                ):
                    vuetify.VIcon("mdi-step-forward")

                # last frame btn
                with vuetify.VBtn(
                    click=self._last,
                    icon=True,
                ):
                    vuetify.VIcon("mdi-step-forward-2")

            return container

    def _first(self):
        self._curr_frame = 1
        self._set_state_var("curr_frame", 1)

        self._animation_scene.GoToFirst()
        self._render_function()

    def _prev(self):
        self._curr_frame = max(1, self._curr_frame - 1)
        self._set_state_var("curr_frame", self._curr_frame)

        self._animation_scene.GoToPrevious()
        self._render_function()

    def _next(self):
        self._curr_frame = min(self._curr_frame + 1, self._num_frames)
        self._set_state_var("curr_frame", self._curr_frame)

        self._animation_scene.GoToNext()
        self._render_function()

    def _last(self):
        self._curr_frame = self._num_frames
        self._set_state_var("curr_frame", self._curr_frame)

        self._animation_scene.GoToLast()
        self._render_function()

    @asynchronous.task
    async def _play(self):
        # reset to first frame if at last frame
        if self._curr_frame == self._num_frames:
            self._first()
            self._state.flush()
            await asyncio.sleep(self.frame_step_time)

        state = self._state
        self._set_state_var("playing", True)
        self._playing = True
        state.flush()
        await asyncio.sleep(0)
        while self._playing:
            self._next()
            self._state.flush()
            await asyncio.sleep(self.frame_step_time)

            if self._curr_frame == self._num_frames:
                self._playing = False
                self._set_state_var("playing", False)
                state.flush()
                await asyncio.sleep(0)

    def _stop(self):
        self._playing = False
        self._set_state_var("playing", False)

    def _set_state_var(self, var, val):
        # prefix state vars with id
        # This allows for multiple instantiations of this class using the same
        # trame state
        self._state[self._get_state_var_name(var)] = val

    def _get_state_var_name(self, var):
        return f"media_ctrl_{self._id}_{var}"
