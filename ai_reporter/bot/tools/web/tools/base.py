from datetime import datetime
import os
from string import Template
from typing import Optional

from selenium.webdriver import ChromeOptions, FirefoxOptions, Remote

from ....image import Image
from ...base import BaseTool
from ..browser import Browser
from ..secret import Secret, SecretType

BROWSER_INFO_TEMPLATE = """
Here is the current state of the web browser...

ACTIVE TAB: $tab_number. $title ($url)
TAB LIST: $tab_list
SCROLL POSITION: x = $sx (${sxp}%), y = $sy (${syp}%)
PAGE SIZE: width = $pw, height = $ph
LAST PAGE LOAD TIME: $page_load_time seconds
AVAILABLE USERNAMES: ${usernames}
"""

class BaseWebTool(BaseTool):

    def __init__(
        self,
        selenium_browser : str = "firefox",
        selenium_url : Optional[str] = None,
        secrets : list[dict] = [],
        screenshot_log_path : Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        # check types
        if selenium_browser: self._check_config_type(selenium_browser, str, "tools.web.selenium_browser")
        if selenium_url: self._check_config_type(selenium_url, str, "tools.web.selenium_url")
        self._check_config_type(secrets, list, "tools.web.secrets")
        if screenshot_log_path: self._check_config_type(screenshot_log_path, str, "tools.web.screenshot_log_path")
        self.browser = self._get_browser(selenium_browser, selenium_url, secrets)
        self.screenshot_log_path = screenshot_log_path

    def _get_browser(self, selenium_browser : str, selenium_url : Optional[str] = None, secrets : list[dict] = []) -> Browser:
        # get previously initialized browser
        if "browser" in self.state and isinstance(self.state["browser"], Browser): return self.state["browser"]
        # init new browser
        remote_driver = None
        if selenium_url:
            opts = FirefoxOptions() if selenium_browser == "firefox" else ChromeOptions()
            remote_driver = Remote(selenium_url, options=opts)
        self.state["browser"] = Browser(driver=remote_driver, secrets=map(lambda s: Secret(**s), secrets))
        return self.state["browser"]

    def _screenshot(self) -> Image:
        screenshot = self.browser.screenshot()
        self._log_screenshot(screenshot)
        out = Image()
        out.contents = screenshot
        return out

    def _log_screenshot(self, screenshot : bytes) -> Optional[str]:
        if not self.screenshot_log_path: return None
        path = os.path.join(self.screenshot_log_path, "web_%d.png" % (
            datetime.now().timestamp(), 
        ))
        with open(path, "wb") as f: f.write(screenshot)
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
        usernames = list(map(lambda s: s.key, filter(lambda s: s.type == SecretType.FORM, secrets)))

        return {
            "sx": sx, "sy": sy, "vw": vw, "vh": vh, "pw": pw, "ph": ph,
            "sxp": sxp, "syp": syp,
            "tab_number": current_window_index+1,
            "url": self.browser.get_current_url(),
            "title": self.browser.get_current_title(),
            "tab_list": ", ".join("%d. %s (%s)" % (i+1, tabs[i]["title"], tabs[i]["url"]) for i in range(len(tabs))),
            "page_load_time": self.browser.last_page_load_time,
            "usernames": (", ".join(usernames)) if usernames else "(none)"
        }

    def _get_browser_window_info_text(self, status_message : str = "") -> str:
        data = self._get_browser_window_info()
        out = Template(BROWSER_INFO_TEMPLATE).substitute(data)
        if status_message: out = "%s\n---\n" % status_message
        return out