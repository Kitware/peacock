import os
from pathlib import Path

from trame.app import get_server
from trame.assets.local import to_url
from trame.ui.vuetify import VAppLayout
from trame.widgets import client, html, simput, vuetify
from trame_simput import get_simput_manager

from peacock_trame import module

from .core.input.LanguageServer import LanguageServerManager
from .executor import Executor
from .exodusViewer import ExodusViewer
from .fileEditor import BlockAdapter, BlockFactory, InputFileEditor


class Peacock:
    def __init__(self, server):
        self.server = server
        server.enable_module(module)

        # Simput
        self.simput_manager = get_simput_manager(
            object_factory=BlockFactory(),
            object_adapter=BlockAdapter(),
        )
        self.simput_widget = simput.Simput(self.simput_manager, trame_server=server)

        # Components
        self.file_editor = InputFileEditor(server, self.simput_manager)
        self.executor = Executor(server)
        self.exodus_viewer = ExodusViewer(server)
        if self.state.lang_server_path:
            LanguageServerManager(server)

        # State
        self.state.trame__title = "peacock-trame"
        self.state.trame__favicon = to_url(
            str(Path(__file__).parent / "logos" / "peacock_logo.ico")
        )

        # Controller
        self.ctrl.simput_reload_data = self.simput_widget.reload_data

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    def ui(self, *args, **kwargs):
        with VAppLayout(self.server) as layout:
            layout.root = self.simput_widget
            client.Style(
                """
                html {
                    overflow:  hidden !important;
                }
            """
            )

            def on_tab_change(tab_idx):
                if tab_idx == 1:
                    self.executor.activate()

                # check for output file when switching to exodus viewer
                if tab_idx == 2:
                    self.exodus_viewer.check_file()

            with html.Div(
                style="position: relative; display: flex; border-bottom: 1px solid gray",
            ):
                html.Img(
                    src=("trame__favicon",),
                    height=50,
                    width=50,
                    style="padding: 5px;",
                )
                with vuetify.VTabs(
                    v_model=("tab_idx", 0),
                    style="z-index: 1;",
                    color="grey",
                    change=(on_tab_change, "[$event]"),
                ):
                    for tab_label in ["Input File", "Execute", "Exodus Viewer"]:
                        vuetify.VTab(tab_label)

                with html.Div(
                    style="position: absolute; top: 0; left: 0; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center;",
                ):
                    with html.Div(
                        v_if=("tab_idx == 0",),
                        style="height: 100%; width: 100%; display: flex; align-items: center; justify-content: flex-end;",
                    ):
                        with vuetify.VBtn(
                            click=self.file_editor.write_file,
                            icon=True,
                            style="z-index: 1;",
                        ):
                            vuetify.VIcon("mdi-content-save-outline")

                    with html.Div(
                        style="height: 100%; width: 300px; display: flex; align-items: center; justify-content: space-between;",
                        v_if=("tab_idx == 1",),
                    ):
                        vuetify.VBtn(
                            "Run",
                            click=self.executor.run,
                            disabled=(
                                "exe_running || exe_use_threading && exe_threads < 2 || exe_use_mpi && exe_processes < 2",
                            ),
                            style="z-index: 1;",
                        )
                        vuetify.VBtn(
                            "Kill",
                            click=self.executor.kill,
                            disabled=("!exe_running",),
                            style="z-index: 1;",
                        )
                        vuetify.VBtn(
                            "Clear",
                            click=self.ctrl.terminal_clear,
                            style="z-index: 1;",
                        )

            # input file editor
            with vuetify.VCol(
                v_show=("tab_idx == 0",), classes="flex-grow-1 pa-0 ma-0"
            ):
                self.file_editor.get_ui()

            # executor
            with vuetify.VCol(
                v_show=("tab_idx == 1",), classes="flex-grow-1 pa-0 ma-0"
            ):
                self.executor.get_ui()

            # exodus viewer
            with vuetify.VCol(
                v_show=("tab_idx == 2",), classes="flex-grow-1 pa-0 ma-0"
            ):
                self.exodus_viewer.get_ui()


def main(server=None, **kwargs):
    # Pop LD_LIBRARY_PATH env variable
    # This caused errors when running the Moose executable on Linux
    # This variable points to paraview/lib which might override our venv/lib
    # These conflicting library files seems to cause the error
    if "LD_LIBRARY_PATH" in os.environ:
        os.environ.pop("LD_LIBRARY_PATH")

    # Get or create server
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

    # Set client type
    server.client_type = "vue2"

    # parse args
    parser = server.cli
    parser.add_argument("-I", "--input", help="Input file (.i)")
    parser.add_argument("-E", "--exe", help="Executable")
    parser.add_argument(
        "-L", "--lang_server", help="Path to language server executable"
    )
    (args, _unknown) = parser.parse_known_args()
    state = server.state
    if args.input is None:
        print("Usage: \n\tpeacock-trame -I /path/to/input/file")
        return
    state.input_file = str(Path(args.input).absolute())
    if args.exe:
        state.executable = str(Path(args.exe).absolute())
    else:
        exec_name = str(Path(args.input).stem) + "-opt"
        state.executable = str(Path(args.input).absolute().parent / exec_name)

    if args.lang_server:
        state.lang_server_path = str(Path(args.lang_server).absolute())

    # Init application
    engine = Peacock(server)
    engine.ui()
    server.controller.on_server_reload.add(engine.ui)

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    main()
