import asyncio
import os
import subprocess

from trame.app import asynchronous
from trame.widgets import html, vuetify, xterm

ANSI_COLORS = dict(
    RESET="\033[0m",
    BOLD="\033[1m",
    DIM="\033[2m",
    RED="\033[31m",
    GREEN="\033[32m",
    YELLOW="\033[33m",
    BLUE="\033[34m",
    MAGENTA="\033[35m",
    CYAN="\033[36m",
    GREY="\033[90m",
    LIGHT_RED="\033[91m",
    LIGHT_GREEN="\033[92m",
    LIGHT_YELLOW="\033[93m",
    LIGHT_BLUE="\033[94m",
    LIGHT_MAGENTA="\033[95m",
    LIGHT_CYAN="\033[96m",
    LIGHT_GREY="\033[37m",
)


class Executor:
    def __init__(self, server):
        self._server = server
        server.state.exe_running = False

    def activate(self):
        self._server.controller.terminal_fit()

    def terminal_print(self, msg, color=None):
        # ANSI color codes for colored terminal output
        if color:
            msg = ANSI_COLORS[color] + msg + ANSI_COLORS["RESET"]

        self._server.controller.terminal_println(msg)

    @asynchronous.task
    async def run(self):
        state, ctrl = self._server.state, self._server.controller

        state.exe_running = True
        state.flush()
        await asyncio.sleep(0)

        args = [state.executable, "-i", state.input_file]
        if state.exe_use_mpi:
            args = ["mpiexec", "-n", str(state.exe_processes)] + args
        if state.exe_use_threading:
            args.append("--n-threads=" + str(state.exe_threads))

        self.terminal_print(f"Running command: {' '.join(args)}", color="MAGENTA")
        self.terminal_print(f"Working directory: {os.getcwd()}", color="MAGENTA")

        self.process = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in self.process.stdout:
            ctrl.terminal_println(line.decode())
            await asyncio.sleep(0)
        self.process.stdout.close()
        state.exe_running = False
        state.flush()
        await asyncio.sleep(0)

    def kill(self):
        self.process.kill()

    def get_ui(self):
        ctrl = self._server.controller
        with html.Div(
            classes="ma-0 pa-0",
            style="position: relative; height: 100%; display: flex; flex-direction: column; align-items: center; max-height: calc(100vh - 51px);",
        ) as executor_ui:
            with html.Div(
                style="position: absolute; top: 0px; width: 100%; display: flex; justify-content: center;",
            ):
                with vuetify.VHover(
                    v_slot="{ hover }",
                    v_if=("!show_executor_settings",),
                ):
                    with vuetify.VBtn(
                        click="show_executor_settings = true",
                        style="""
                            min-width: 50px;
                            min-height: 0px;
                            height: auto;
                            padding: 2px;
                            border-radius: 0px 0px 4px 4px;
                            z-index: 3;
                        """,
                    ):
                        with html.Div(style="display: flex; flex-direction: column;"):
                            vuetify.VIcon("mdi-chevron-down", style="height: 15px;")
                            with vuetify.VSlideYTransition():
                                vuetify.VIcon(
                                    "mdi-cog-outline",
                                    v_if="hover",
                                    style="padding-top: 15px;",
                                )
            with html.Div(
                style="position: relative; width: 500px;",
                v_show=("show_executor_settings", False),
            ):
                with vuetify.VRow(
                    dense=True,
                    justify="center",
                ):
                    with vuetify.VCol(cols=5):
                        vuetify.VSwitch(
                            label="Use MPI",
                            v_model=("exe_use_mpi", False),
                        )
                    with vuetify.VCol(cols=3):
                        vuetify.VTextField(
                            label="Processes",
                            type="number",
                            v_model=("exe_processes", 2),
                            rules=("[value => value > 0 || 'Must be > 0']",),
                            disabled=("!exe_use_mpi",),
                        )

                with vuetify.VRow(
                    dense=True,
                    justify="center",
                ):
                    with vuetify.VCol(cols=5):
                        vuetify.VSwitch(
                            label="Use Threading",
                            v_model=("exe_use_threading", False),
                        )
                    with vuetify.VCol(cols=3):
                        vuetify.VTextField(
                            label="Threads",
                            type="number",
                            v_model=("exe_threads", 2),
                            rules=("[value => value > 0 || 'Must be > 0']",),
                            disabled=("!exe_use_threading",),
                        )

                with html.Div(
                    style="position: absolute; bottom: 0px; width: 100%; display: flex; justify-content: center;",
                ):
                    with vuetify.VHover(
                        v_slot="{ hover }",
                    ):
                        with vuetify.VBtn(
                            click="show_executor_settings = false",
                            style="min-width: 50px; min-height: 0px; height: auto; padding: 2px; border-radius: 0px 0px 4px 4px; z-index: 3;",
                        ):
                            with html.Div(
                                style="display: flex; flex-direction: column;"
                            ):
                                with vuetify.VSlideYReverseTransition():
                                    vuetify.VIcon(
                                        "mdi-cog-off-outline",
                                        v_if="hover",
                                    )
                                vuetify.VIcon("mdi-chevron-up", style="height: 15px;")

            with html.Div(
                style=(
                    """{
                    height: show_executor_settings ? 'calc(100% - 150px)' : 'calc(100% - 8px)',
                    width: '100%',
                    padding: '8px',
                    paddingTop: '0px',
                    marginTop: show_executor_settings ? '0px' : '25px'
                }""",
                ),
            ):
                term = xterm.XTerm(options="{ disableStdin: 0 }")
                ctrl.terminal_println = term.writeln
                ctrl.terminal_clear = term.clear
                ctrl.terminal_fit = term.fit

        return executor_ui
