from trame_client.widgets.core import AbstractElement
from .. import module


class HtmlElement(AbstractElement):
    def __init__(self, _elem_name, children=None, **kwargs):
        super().__init__(_elem_name, children, **kwargs)
        if self.server:
            self.server.enable_module(module)


class Editor(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(
            "editor",
            **kwargs,
        )
        self._attr_names += [
            "contents",
            "filepath",
        ]
        self._event_names += [
            "change",
        ]


class Terminal(HtmlElement):
    _next_id = 0

    def __init__(self, **kwargs):
        Terminal._next_id += 1
        self._ref = kwargs.get('ref', f"terminal_{Terminal._next_id}")
        super().__init__(
            "terminal",
            **{
                **kwargs,
                'ref': self._ref
            }
        )

    def write(self, string):
        self.server.js_call(self._ref, "write", string)
