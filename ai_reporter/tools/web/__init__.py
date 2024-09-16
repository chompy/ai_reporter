import base64
import datetime
import logging
import os
from string import Template
from typing import Iterable, Optional

from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionContentPartTextParam
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from selenium.webdriver import ChromeOptions, FirefoxOptions, Remote

from ...utils import dict_get_type
from ..base import BaseTool
from ..response import ToolPromptResponse
from .browser import Browser, HEIGHT, WIDTH
from .secret import SecretType
from .secret import Secret
from .tools import AVAILABLE_TOOLS

DEFAULT_SYSTEM_PROMPT = """
You will be given screenshots from a web browser and given access to tools that will allow you to interact with the web browser.
Using the tools provided perform the user's task or answer their question.

When you are finished use the `done` tool.

IMPORTANT NOTES:
- The viewport size is ${viewport_w}x${viewport_h} pixels.
- Every interactable element has been given a two character label. You will reference these labels when making tool calls.
- Use the `done` as soon as you have performed the task asked of you OR gathered enough information to form a conclusion.
- You might need to scroll around the page to find what you're looking for. It's recommended to scroll vertically at increments of ${viewport_h}.
- The user will provide an updated screenshot after all tool functions have been executed. It's often best to perform one tool call at a time to ensure you are working with the latest context.
- Use the `element` tool to get the list of options for a SELECT element (dropdown).
- Using the `click` tool can sometimes open a new tab. Tabs are numbered and can be accessed using the `switch_to` tool with the associated number. The tab list should contain more than one option when a new tab is opened (the original tab and the new one). If the tab list only contains one item then a new tab was not opened.
- When submitting a form use the `submit` tool instead of clicking a button.
"""

BROWSER_INFO_TEMPLATE = """
Here is the current state of the web browser...

ACTIVE TAB: $tab_number. $title ($url)
TAB LIST: $tab_list
SCROLL POSITION: x = $sx (${sxp}%), y = $sy (${syp}%)
PAGE SIZE: width = $pw, height = $ph
LAST PAGE LOAD TIME: $page_load_time seconds
AVAILABLE USERNAMES: ${usernames}
"""

class WebTool(BaseTool):

    def __init__(
        self,
        available_urls : Optional[Iterable[str]] = None,
        secrets : Optional[Iterable[Secret]] = None,
        selenium_browser : str = "firefox",
        selenium_remote_url : Optional[str] = None,
        screenshot_log_path : Optional[str] = None,
        system_prompt : Optional[str] = None,
        max_iterations : Optional[int] = None,
        max_error_retries : Optional[int] = None,
        logger : Optional[logging.Logger] = None,
        **kwargs
    ):
    
        super().__init__(logger=logger)
        self.args = {}
        self.available_urls = available_urls
        self.browser = self._get_browser(selenium_browser, remote_url=selenium_remote_url, secrets=secrets)
        self.max_iterations = max_iterations
        self.max_error_retries = max_error_retries
        self.system_prompt = Template(system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT).substitute({
            "viewport_w": WIDTH,
            "viewport_h": HEIGHT
        })
        self.screenshot_log_path = screenshot_log_path

    @staticmethod
    def name() -> str:
        return "web"

    @classmethod
    def definition(cls, available_urls : Optional[Iterable[str]] = None, **kwargs) -> dict:
        enum_urls = {}
        if available_urls:
            enum_urls["enum"] = list(available_urls)
        return {
            "name": cls.name(),
            "description": "Ask a large language model to perform a task in a web browser and report on its findings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The starting URL.",
                        **enum_urls
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Prompt for the large language model."
                    }
                },
                "required": ["url", "prompt"]
            }
        }

    def execute(self, **kwargs):
        super(self.__class__, self).execute(**kwargs)
        self.browser.goto(dict_get_type(kwargs, "url", str))
        # build prompt for web bot
        return ToolPromptResponse(
            user_prompt=dict_get_type(kwargs, "prompt", str),
            system_prompt=self.system_prompt,
            max_iterations=self.max_iterations if self.max_iterations else 15,
            max_error_retry=self.max_error_retries if self.max_error_retries else 3,
            tools=dict(map(lambda t: (t.name(), {"browser": self.browser}), AVAILABLE_TOOLS)),
            pre_iteration_callback=self._browser_callback
        )

    def _get_browser(self, name : str, remote_url : Optional[str] = None, secrets : Optional[Iterable[Secret]] = None) -> Browser:
        remote_driver = None
        if remote_url:
            opts = FirefoxOptions() if name == "firefox" else ChromeOptions()
            remote_driver = Remote(remote_url, options=opts)
        return Browser(driver=remote_driver, secrets=secrets)

    def _browser_callback(self, iteration : int, messages : list[ChatCompletionMessageParam]) -> list[ChatCompletionMessageParam]:
        screenshot = self.browser.screenshot()
        browser_info = self._get_browser_window_info()
        info_text = Template(BROWSER_INFO_TEMPLATE).substitute(browser_info)
        screenshot_path = self._log_screenshot(screenshot, iteration)
        if self.logger:
            self.logger.info(
                "Collect browser information.", extra={
                    "action": "browser info", "object": "", "parameters": browser_info | {"screenshot_path": screenshot_path}
                }
            )
        return [
            ChatCompletionUserMessageParam(
                content=[
                    ChatCompletionContentPartTextParam(text=info_text, type="text"),
                    ChatCompletionContentPartImageParam(image_url=ImageURL(url=screenshot), type="image_url")
                ],
                role="user",
                name="web browser"
            )
        ]
        
    def _log_screenshot(self, screenshot_b64 : str, iteration : int) -> Optional[str]:
        if not self.screenshot_log_path: return None
        path = os.path.join(self.screenshot_log_path, "web_%d_%d.png" % (
            datetime.datetime.now().timestamp(), iteration
        ))
        screenshot_b64 = screenshot_b64.split(",")[1]
        with open(path, "wb") as f:
            f.write(base64.b64decode(screenshot_b64))
        return path

    def _get_browser_window_info(self) -> dict:
        (sx, sy) = self.browser.get_scroll_position()
        (vw, vh) = self.browser.get_viewport_size()
        (pw, ph) = self.browser.get_page_size()

        sxp = int((float(sx) / (float(pw) - float(vw))) * 100.0) if pw > vw else 0
        syp = int((float(sy) / (float(ph) - float(vh))) * 100.0) if ph > vh else 0

        current_window_index = 0
        tabs = self.browser.get_open_windows()
        for i in range(len(tabs)):
            if tabs[i]["handle"] == self.browser.get_current_window(): current_window_index = i
        
        secrets = self.browser.get_secrets_for_current_url()
        usernames = map(lambda s: s.key, filter(lambda s: s.type == SecretType.FORM, secrets))

        return {
            "sx": sx, "sy": sy, "vw": vw, "vh": vh, "pw": pw, "ph": ph,
            "sxp": sxp, "syp": syp,
            "tab_number": current_window_index+1,
            "url": self.browser.get_current_url(),
            "title": self.browser.get_current_title(),
            "tab_list": ", ".join("%d. %s (%s)" % (i+1, tabs[i]["title"], tabs[i]["url"]) for i in range(len(tabs))),
            "page_load_time": self.browser.last_page_load_time,
            "usernames": ", ".join(usernames)
        }
