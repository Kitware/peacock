import os
import socket
import subprocess

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError
from trame.app import asynchronous

import peacock_trame


class LanguageServerManager:
    def __init__(self, trame_server):
        self.server = trame_server
        state = trame_server.state

        @trame_server.trigger("trame_lang_server")
        def on_lang_server(type, event):
            # print("LANG CLIENT MSG: ", type, event)
            if type == "send":
                self.send_to_lang_server(event)
            if type == "close":
                self.ws.close()

        # use socket bound to port 0 to find random open port
        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()

        # start language server
        # TODO: kill child process after unexpected exit
        ls_middleware_path = os.path.join(
            os.path.dirname(peacock_trame.__file__),
            "lang-server",
            "ls-middleware.js",
        )
        subprocess.Popen(
            [
                "node",
                ls_middleware_path,
                state.lang_server_path,
                str(port),
                "--stdio",
            ]
        )

        self.url = f"ws://localhost:{port}"
        self.init_ws()

    @asynchronous.task
    async def init_ws(self):
        async with aiohttp.ClientSession() as client:
            self.client = client
            connected = False
            while not connected:
                try:
                    async with client.ws_connect(self.url, max_msg_size=0) as ws:
                        self.ws = ws
                        self.send_to_client({"type": "open"})
                        connected = True
                        async for msg in ws:
                            # print("LANG SERVER MSG: ", msg.data)
                            if msg.type == aiohttp.WSMsgType.CLOSE:
                                break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                print(msg.data)
                                pass
                            else:
                                self.send_to_client(
                                    {"type": "message", "data": msg.data}
                                )

                except ClientConnectionError:
                    pass

    @asynchronous.task
    async def send_to_lang_server(self, msg):
        await self.ws.send_str(msg)

    def send_to_client(self, msg):
        self.server.protocol.publish("trame.lang.server", msg)
