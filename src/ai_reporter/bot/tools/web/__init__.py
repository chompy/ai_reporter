from .tools.goto import WebGotoTool
from .tools.element import WebElementTool
from .tools.click import WebClickTool
from .tools.hover import WebHoverTool
from .tools.scroll import WebScrollTool
from .tools.input import WebInputTool
from .tools.password import WebPasswordTool
from .tools.select import WebSelectTool
from .tools.switch_tab import WebSwitchTabTool

TOOLS = [
    WebGotoTool,
    WebElementTool,
    WebClickTool,
    WebHoverTool,
    WebScrollTool,
    WebInputTool,
    WebPasswordTool,
    WebSelectTool,
    WebSwitchTabTool
]