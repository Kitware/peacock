# add moose/python to sys path
import sys
import os
moose_dir = os.environ.get("MOOSE_DIR", None)
sys.path.append(os.path.join(moose_dir, 'python'))

from trame.app import get_server, dev
from trame.ui.vuetify import VAppLayout
from trame.widgets import vuetify, html

from .input.fileEditor import InputFileEditor


def _reload():
    server = get_server()
    dev.reload(InputFileEditor)
    initialize(server)


def initialize(server):
    file_editor = InputFileEditor(server)

    server.state.trame__title = "peacock-trame"

    with VAppLayout(server) as layout:

        # Main content
        with layout:
            with vuetify.VContainer(fluid=True, classes="pa-0 fill-height d-flex flex-column"):
                with vuetify.VContainer(fluid=True, classes="pa-0 flex-grow-0"):
                    with vuetify.VMenu():
                        with vuetify.Template(v_slot_activator="{on, attrs}"):
                            vuetify.VBtn('Peacock', v_bind="attrs", v_on="on")

                        with vuetify.VList():
                            vuetify.VListItem("List Item")
                            vuetify.VListItem("Preferences")
                            vuetify.VListItem("Exit")

                    with vuetify.VMenu():
                        with vuetify.Template(v_slot_activator="{on, attrs}"):
                            vuetify.VBtn('Input File', v_bind="attrs", v_on="on")

                        with vuetify.VList():
                            with vuetify.VListItem("Open", click="console.log($refs.fileInput); $refs.fileInput.$children[0].$el.click()"):
                                vuetify.VFileInput(v_model=("input_file", None), type="file", classes="d-none", ref="fileInput")
                            vuetify.VListItem("Recently opened")
                            vuetify.VListItem("Save")
                            vuetify.VListItem("Save As")
                            vuetify.VListItem("Clear")
                            vuetify.VListItem("Check")
                            vuetify.VListItem("View current input file")
                            vuetify.VListItem("Background")

                    with vuetify.VMenu():
                        with vuetify.Template(v_slot_activator="{on, attrs}"):
                            vuetify.VBtn('E<u>x</u>ecute', tile="true", v_bind="attrs", v_on="on")

                        with vuetify.VList():
                            vuetify.VListItem("Recent working dirs")
                            vuetify.VListItem("Recent executables")
                            vuetify.VListItem("Recent arguments")
                            vuetify.VListItem("Reload executable syntax")

                    with vuetify.VMenu():
                        with vuetify.Template(v_slot_activator="{on, attrs}"):
                            vuetify.VBtn('<u>R</u>esults', v_bind="attrs", v_on="on")

                        with vuetify.VList():
                            vuetify.VListItem("Background")
                            with vuetify.VListItem():
                                vuetify.VCheckbox()
                                html.P("Show live script", classes="ma-0")
                            vuetify.VListItem("Export")

                    with vuetify.VMenu():
                        with vuetify.Template(v_slot_activator="{on, attrs}"):
                            vuetify.VBtn('Debug', v_bind="attrs", v_on="on")

                        with vuetify.VList():
                            vuetify.VListItem("Show Python Console")

                with vuetify.VTabs(classes="flex-grow-0", v_model=("tab_idx", 0)):
                    for tab_label in ['Input File', 'Execute', 'Exodus Viewer', 'Postprocess Viewer', 'Vector Postprocess Viewer']:
                        vuetify.VTab(tab_label)

                # input file editor
                with vuetify.VContainer(v_if="tab_idx == 0", fluid=True, classes="flex-grow-1 pa-0 ma-0"):
                    file_editor.get_ui()


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
    (args, _unknown) = parser.parse_known_args()
    state = server.state
    if args.input is None or args.exe is None:
        print("Usage: \n\tpeacock-trame -I /path/to/input/file -E /path/to/executable [options]")
        return
    state.input_file = args.input
    state.executable = args.exe

    # Make UI auto reload
    server.controller.on_server_reload.add(_reload)

    # Init application
    initialize(server)

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    main()
