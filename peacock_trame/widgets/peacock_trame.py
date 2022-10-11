from trame_client.widgets.core import AbstractElement
from .. import module


class HtmlElement(AbstractElement):
    def __init__(self, _elem_name, children=None, **kwargs):
        super().__init__(_elem_name, children, **kwargs)
        if self.server:
            self.server.enable_module(module)


# Expose your vue component(s)
class CustomWidget(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(
            "your-custom-widget",
            **kwargs,
        )
        self._attr_names += [
            "attribute_name",
            ("py_attr_name", "js_attr_name"),
        ]
        self._event_names += [
            "click",
            "change",
        ]
