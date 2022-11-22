# add moose/python to sys path
import sys
import os
moose_dir = os.environ.get("MOOSE_DIR", None)
sys.path.append(os.path.join(moose_dir, 'python'))

from trame.app import get_server, dev
from trame.ui.vuetify import VAppLayout
from trame.widgets import vuetify, html, simput
from trame_simput import get_simput_manager

from peacock_trame import module

from .fileEditor import (
    InputFileEditor,
    BlockFactory,
    BlockAdapter,
)
from .executor import (
    Executor,
)

def _reload():
    server = get_server()
    dev.reload(InputFileEditor)
    initialize(server)


def initialize(server):
    state, ctrl = server.state, server.controller

    server.enable_module(module)

    state.trame__title = "peacock-trame"

    simput_manager = get_simput_manager(
        object_factory=BlockFactory(),
        object_adapter=BlockAdapter(),
    )
    simput_widget = simput.Simput(simput_manager, trame_server=server)

    file_editor = InputFileEditor(server, simput_manager)
    executor = Executor(server)

    ctrl.reload_simput = simput_widget.reload_data

    with VAppLayout(server) as layout:

        layout.root = simput_widget

        with vuetify.VTabs(
            v_model=("tab_idx", 0),
            centered=True,
            classes="flex-grow-0",
            color='grey',
            style="border-bottom: 1px solid gray",
        ):
            for tab_label in ['Input File', 'Execute',]:
                vuetify.VTab(tab_label)

        # input file editor
        with vuetify.VCol(v_show=("tab_idx == 0",), classes="flex-grow-1 pa-0 ma-0"):
            file_editor.get_ui()
        with html.Div(
            v_if=("tab_idx == 0",),
            style="position: absolute; top: 10px; right: 10px; display: flex;",
        ):
            with vuetify.VBtn(
                click=file_editor.write_file,
                icon=True,
            ):
                vuetify.VIcon('mdi-content-save-outline')
            with vuetify.VBtn(
                click=file_editor.toggle_editor,
                icon=True,
            ):
                vuetify.VIcon(
                    'mdi-file-document-edit',
                    v_if=("show_file_editor",),
                ),
                vuetify.VIcon(
                    'mdi-file-document-edit-outline',
                    v_if=("!show_file_editor",),
                )

        # executor
        with vuetify.VCol(v_show=("tab_idx == 1",), classes="flex-grow-1 pa-0 ma-0"):
            executor.get_ui()


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
    parser.add_argument("-o", "--output", help="Output simput model yaml file")
    (args, _unknown) = parser.parse_known_args()
    state = server.state
    if args.input is None or args.exe is None:
        print("Usage: \n\tpeacock-trame -I /path/to/input/file -E /path/to/executable [options]")
        return
    state.input_file = args.input
    state.executable = args.exe
    state.model_file = args.output

    # Make UI auto reload
    server.controller.on_server_reload.add(_reload)

    # Init application
    initialize(server)

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    main()
