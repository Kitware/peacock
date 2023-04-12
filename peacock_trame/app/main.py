import os

from trame.app import dev, get_server
from trame.assets.local import LocalFileManager
from trame.ui.vuetify import VAppLayout
from trame.widgets import html, simput, vuetify
from trame_simput import get_simput_manager

from peacock_trame import module

from .core.input.LanguageServer import LanguageServerManager
from .executor import Executor
from .exodusViewer import ExodusViewer
from .fileEditor import BlockAdapter, BlockFactory, InputFileEditor


def _reload():
    server = get_server()
    dev.reload(InputFileEditor)
    initialize(server)


def initialize(server):
    state, ctrl = server.state, server.controller

    server.enable_module(module)

    state.trame__title = "peacock-trame"

    favicons = LocalFileManager(__file__)
    favicons.url("peacock_logo", "./logos/peacock_logo.ico")
    state.trame__favicon = favicons["peacock_logo"]

    simput_manager = get_simput_manager(
        object_factory=BlockFactory(),
        object_adapter=BlockAdapter(),
    )
    simput_widget = simput.Simput(simput_manager, trame_server=server)

    file_editor = InputFileEditor(server, simput_manager)
    executor = Executor(server)
    exodus_viewer = ExodusViewer(server)

    ctrl.simput_reload_data = simput_widget.reload_data

    if state.lang_server_path:
        LanguageServerManager(server)

    with VAppLayout(server) as layout:
        layout.root = simput_widget

        def on_tab_change(tab_idx):
            # check for output file when switching to exodus viewer
            if tab_idx == 2:
                exodus_viewer.check_file()

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
                        click=file_editor.write_file, icon=True, style="z-index: 1;"
                    ):
                        vuetify.VIcon("mdi-content-save-outline")

                with html.Div(
                    style="height: 100%; width: 300px; display: flex; align-items: center; justify-content: space-between;",
                    v_if=("tab_idx == 1",),
                ):
                    vuetify.VBtn(
                        "Run",
                        click=executor.run,
                        disabled=(
                            "exe_running || exe_use_threading && exe_threads < 2 || exe_use_mpi && exe_processes < 2",
                        ),
                        style="z-index: 1;",
                    )
                    vuetify.VBtn(
                        "Kill",
                        click=executor.kill,
                        disabled=("!exe_running",),
                        style="z-index: 1;",
                    )
                    vuetify.VBtn(
                        "Clear",
                        click=ctrl.clear_terminal,
                        style="z-index: 1;",
                    )

        # input file editor
        with vuetify.VCol(v_show=("tab_idx == 0",), classes="flex-grow-1 pa-0 ma-0"):
            file_editor.get_ui()

        # executor
        with vuetify.VCol(v_show=("tab_idx == 1",), classes="flex-grow-1 pa-0 ma-0"):
            executor.get_ui()

        # exodus viewer
        with vuetify.VCol(v_show=("tab_idx == 2",), classes="flex-grow-1 pa-0 ma-0"):
            exodus_viewer.get_ui()


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

    # parse args
    parser = server.cli
    parser.add_argument("-I", "--input", help="Input file (.i)")
    parser.add_argument("-E", "--exe", help="Executable")
    parser.add_argument(
        "-L", "--lang_server", help="Path to language server executable"
    )
    (args, _unknown) = parser.parse_known_args()
    state = server.state
    if args.input is None or args.exe is None:
        print(
            "Usage: \n\tpeacock-trame -I /path/to/input/file -E /path/to/executable [options]"
        )
        return
    state.input_file = os.path.abspath(args.input)
    state.executable = os.path.abspath(args.exe)
    if args.lang_server:
        state.lang_server_path = os.path.abspath(args.lang_server)

    # Make UI auto reload
    server.controller.on_server_reload.add(_reload)

    # Init application
    initialize(server)

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    main()
