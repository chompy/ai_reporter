# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from ai_reporter.bot.tools.web.tools.click import WebClickTool
from ai_reporter.bot.tools.web.tools.element import WebElementTool
from ai_reporter.bot.tools.web.tools.goto import WebGotoTool
from ai_reporter.bot.tools.web.tools.hover import WebHoverTool
from ai_reporter.bot.tools.web.tools.input import WebInputTool
from ai_reporter.bot.tools.web.tools.password import WebPasswordTool
from ai_reporter.bot.tools.web.tools.scroll import WebScrollTool
from ai_reporter.bot.tools.web.tools.select import WebSelectTool
from ai_reporter.bot.tools.web.tools.switch_tab import WebSwitchTabTool

TOOLS = [
    WebGotoTool,
    WebElementTool,
    WebClickTool,
    WebHoverTool,
    WebScrollTool,
    WebInputTool,
    WebPasswordTool,
    WebSelectTool,
    WebSwitchTabTool,
]
