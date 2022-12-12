import subprocess
import asyncio

from trame.widgets import vuetify, html
from trame.app import asynchronous

from peacock_trame.widgets import peacock


class Executor():
    def __init__(self, server):
        self._server = server
        self.exe_path = server.state.executable

    @asynchronous.task
    async def run(self):
        state, ctrl = self._server.state, self._server.controller
        state.exe_running = True
        state.flush()
        await asyncio.sleep(0)
        process = subprocess.Popen([self.exe_path, '-i', state.input_file], stdout=subprocess.PIPE)
        for line in process.stdout:
            ctrl.write_to_terminal(line.decode())
            await asyncio.sleep(0)
        process.stdout.close()
        state.exe_running = False
        state.flush()
        await asyncio.sleep(0)

    def get_ui(self):
        ctrl = self._server.controller
        executor_ui = vuetify.VCol(
            classes="ma-0 pa-0",
            style="height: 100%; display: flex; flex-direction: column;",
        )

        with executor_ui:
            with html.Div(classes="pa-1", style="display: flex; justify-content: center;"):
                vuetify.VBtn(
                    "Run",
                    click=self.run,
                    disabled=("exe_running", False),
                )
            with html.Div(classes="pa-2", style="flex: 1 1 0px; width: 100%;"):
                term = peacock.Terminal()
                ctrl.write_to_terminal = term.write
