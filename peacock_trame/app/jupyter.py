from trame.app import get_server, jupyter

from peacock_trame.app import engine, ui


def show(server=None, **kwargs):
    """Run and display the trame application in jupyter's event loop

    The kwargs are forwarded to IPython.display.IFrame()
    """
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

    # Disable logging
    import logging

    engine_logger = logging.getLogger("peacock_trame.app.engine")
    engine_logger.setLevel(logging.WARNING)

    # Initialize app
    engine.initialize(server)
    ui.initialize(server)

    # Show as cell result
    jupyter.show(server, **kwargs)


def jupyter_proxy_info():
    """Get the config to run the trame application via jupyter's server proxy

    This is provided to the `jupyter_serverproxy_servers` entrypoint, and the
    jupyter server proxy will use it to start the application as a separate
    process.
    """
    return {
        "command": ["peacock-trame", "-p", "0", "--server"],
    }
