from trame_client.widgets.core import AbstractElement

from .. import module

__all__ = ["Editor"]


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
