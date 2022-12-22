import subprocess
import asyncio
import os

from trame.widgets import vuetify, html
from trame.app import asynchronous

from peacock_trame.widgets import peacock


class Executor():
    def __init__(self, server):
        self._server = server

        server.state.exe_running = False

    def terminal_print(self, msg, color=None):
        # ANSI color codes for colored terminal output
        color_codes = dict(RESET='\033[0m',
                           BOLD='\033[1m',
                           DIM='\033[2m',
                           RED='\033[31m',
                           GREEN='\033[32m',
                           YELLOW='\033[33m',
                           BLUE='\033[34m',
                           MAGENTA='\033[35m',
                           CYAN='\033[36m',
                           GREY='\033[90m',
                           LIGHT_RED='\033[91m',
                           LIGHT_GREEN='\033[92m',
                           LIGHT_YELLOW='\033[93m',
                           LIGHT_BLUE='\033[94m',
                           LIGHT_MAGENTA='\033[95m',
                           LIGHT_CYAN='\033[96m',
                           LIGHT_GREY='\033[37m')
        if color:
            msg = color_codes[color] + msg + color_codes['RESET']

        self._server.controller.write_to_terminal(msg)

    @asynchronous.task
    async def run(self):
        state, ctrl = self._server.state, self._server.controller

        state.exe_running = True
        state.flush()
        await asyncio.sleep(0)

        args = [state.executable, '-i', state.input_file]
        if state.exe_use_mpi:
            args = ['mpiexec', '-n', str(state.exe_processes)] + args
        if state.exe_use_threading:
            args.append('--n-threads=' + str(state.exe_threads))

        self.terminal_print(f"Running command: {' '.join(args)}", color="MAGENTA")
        self.terminal_print(f"Working directory: {os.getcwd()}", color="MAGENTA")

        self.process = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in self.process.stdout:
            ctrl.write_to_terminal(line.decode())
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
            style="height: 100%; display: flex; flex-direction: column; align-items: center;",
        ) as executor_ui:
            with html.Div(
                style="width: 500px;"
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
                            rules=("[value => value > 1 || 'Must be > 1']",),
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
                            rules=("[value => value > 1 || 'Must be > 1']",),
                            disabled=("!exe_use_threading",),
                        )

                with vuetify.VRow(
                    dense=True,
                    justify="center",
                ):
                    vuetify.VBtn(
                        "Run",
                        click=self.run,
                        disabled=("exe_running || exe_use_threading && exe_threads < 2 || exe_use_mpi && exe_processes < 2",),
                        style="margin-right: 35px;",
                    )
                    vuetify.VBtn(
                        "Kill",
                        click=self.kill,
                        disabled=("!exe_running",),
                        style="margin-right: 35px;",
                    )
                    vuetify.VBtn(
                        "Clear",
                        click=ctrl.clear_terminal,
                    )

            with html.Div(classes="pa-2", style="flex: 1 1 0px; width: 100%;"):
                term = peacock.Terminal()
                ctrl.write_to_terminal = term.write
                ctrl.clear_terminal = term.clear

        return executor_ui
