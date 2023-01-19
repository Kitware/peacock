import os

from trame.app import get_server, dev
from trame.ui.vuetify import VAppLayout
from trame.widgets import vuetify, html, simput
from trame_simput import get_simput_manager
from trame.assets.local import LocalFileManager

from peacock_trame import module
from .core.input.LanguageServer import LanguageServerManager

from .fileEditor import (
    InputFileEditor,
    BlockFactory,
    BlockAdapter,
)
from .executor import Executor
from .exodusViewer import ExodusViewer


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

        with html.Div(style="display: flex; border-bottom: 1px solid gray",):
            html.Img(
                src=("trame__favicon",),
                height=50,
                width=50,
                style="padding: 5px;",
            )
            with vuetify.VTabs(
                v_model=("tab_idx", 0),
                classes="flex-grow-0",
                color='grey',
                change=(on_tab_change, "[$event]"),
            ):
                for tab_label in ['Input File', 'Execute', 'Exodus Viewer']:
                    vuetify.VTab(tab_label)

        # input file editor
        with vuetify.VCol(v_show=("tab_idx == 0",), classes="flex-grow-1 pa-0 ma-0"):
            file_editor.get_ui()
        with html.Div(
            v_show=("tab_idx == 0",),
            style="position: absolute; top: 10px; right: 10px; display: flex;",
        ):
            with vuetify.VBtn(
                click=file_editor.write_file,
                icon=True,
            ):
                vuetify.VIcon('mdi-content-save-outline')

        # executor
        with vuetify.VCol(v_show=("tab_idx == 1",), classes="flex-grow-1 pa-0 ma-0"):
            executor.get_ui()

        # exodus viewer
        with vuetify.VCol(v_show=("tab_idx == 2",), classes="flex-grow-1 pa-0 ma-0"):
            exodus_viewer.get_ui()


def main(server=None, **kwargs):
    # Get or create server
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

    # parse args
    parser = server.cli
    parser.add_argument("-I", "--input", help="Input file (.i)")
    parser.add_argument("-E", "--exe", help="Executable")
    parser.add_argument("-L", "--lang_server", help="Path to language server executable")
    (args, _unknown) = parser.parse_known_args()
    state = server.state
    if args.input is None or args.exe is None:
        print("Usage: \n\tpeacock-trame -I /path/to/input/file -E /path/to/executable [options]")
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
