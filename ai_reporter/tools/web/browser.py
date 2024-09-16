import io
import base64
import math
import time
from typing import Iterable, Optional
from fnmatch import fnmatch
from urllib.parse import urlparse, quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from ...error.web import ElementNotFoundException, InvalidElementException
from .secret import Secret, SecretType

WIDTH = 1280
HEIGHT = 768
ACTION_WAIT_TIME=1

class Browser:

    def __init__(self, driver : Optional[WebDriver] = None, secrets : Optional[Iterable[Secret]] = None):
        self.driver = driver if driver else webdriver.Firefox() # default firefox
        self.driver.set_window_size(WIDTH, HEIGHT)
        self.driver.implicitly_wait(5)
        self.element_labels = {}
        self.window_list = []
        self.last_page_load_time = 0
        self.secrets = list(secrets if secrets else [])
        self._last_input_element = None

    def __del__(self):
        if self.driver: self.close()
    
    def _define_element_labels(self):
        self.element_labels = {}
        label_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href],input,textarea,select,button")
        counter = 0
        for element in label_elements:
            if not element.is_displayed() or not element.is_enabled(): continue
                        
            s1 = chr(65 + int(math.floor(counter / 9.0)) )
            s2 = (counter % 9) + 1
            counter += 1
            self.element_labels["%s%d" % (s1, s2)] = element

    def _get_element(self, label : str) -> WebElement:
        element = self.element_labels.get(label)
        if not element: raise ElementNotFoundException("Unable to find element labeled '%s'." % label)
        return element

    def _wait(self):
        time.sleep(ACTION_WAIT_TIME)

    def _wait_for_load(self):
        while self.driver.execute_script("return document.readyState") != "complete":
            time.sleep(1)
            
    def get_element_info(self, label : str) -> dict:
        """
        Get information about an element.
        :param label: Element label.
        """

        element = self._get_element(label)
        out = {
            "TAG NAME": element.tag_name
        }

        # ID
        attr_id = element.get_attribute("id")
        if attr_id: out["ID"] = attr_id

        # tag specific details        
        match(element.tag_name):
            # TAG: A
            case "a":
                attr_href = element.get_attribute("href")
                if attr_href: out["A HREF"] = attr_href
                attr_target = element.get_attribute("target")
                if attr_target: out["A TARGET"] = attr_target
                out["A inner text"] = element.text if element.text else "(none)"

            # TAG: INPUT
            case "input":
                attr_type = element.get_attribute("type")
                if attr_type: out["INPUT TYPE"] = attr_type
                attr_value = element.get_attribute("value")
                if attr_value: out["INPUT VALUE"] = attr_value

            # TAG: SELECT
            case "select":
                options = []
                option_elements = element.find_elements(By.TAG_NAME, "option")
                for option_element in option_elements:
                    options.append(option_element.text)
                out["SELECT OPTIONS"] = ",".join(options)

        return out

    def get_current_url(self) -> str:
        """Get URL for current browser window/tab."""
        purl = urlparse(self.driver.current_url)
        if (purl.username or purl.password) and purl.hostname:
            return purl.scheme + "://" + self.driver.current_url[self.driver.current_url.find(purl.hostname):]
        return self.driver.current_url

    def get_current_title(self) -> str:
        """Get title for current browser window/tab."""
        return self.driver.title

    def get_current_window(self) -> str:
        """Get the handle (UID) of the current browser window/tab."""
        return self.driver.current_window_handle

    def get_open_windows(self) -> list[dict]:
        """Get list of open browser windows/tabs."""
        if self.window_list: return self.window_list
        self.window_list = []
        current_wh = "%s" % self.driver.current_window_handle
        for wh in self.driver.window_handles:
            self.driver.switch_to.window(wh)
            self.window_list.append({
                "url": self.get_current_url(),
                "title": self.driver.title,
                "handle": wh
            })
        self.driver.switch_to.window(current_wh)
        return self.window_list

    def switch_window(self, handle : str):
        """
        Switch active window/tab.
        :param handle: Handle of the window/tab to switch to.
        """
        self.driver.switch_to.window(handle)
        self._wait()
        self._define_element_labels()

    def goto(self, url : str):
        """
        Open given URL.
        :param url: URL to open.
        """
        start = time.time()
        self.window_list = []

        for secret in self.get_secrets_for_url(url):
            if secret.type == SecretType.HTTP_BASIC:
                url = self._add_basic_auth_to_url(url, secret.key, secret.value)
                break

        self.driver.get(url)
        self._wait_for_load()
        self._define_element_labels()
        self.last_page_load_time = time.time() - start
        self._last_input_element = None

    def click(self, label : str):
        """
        Click on element with given label.
        :param label: Element label.
        """
        start = time.time()
        current_url = self.driver.current_url
        self.window_list = []
        current_handle = self.driver.current_window_handle

        self._get_element(label).click()
        self._wait_for_load()

        self.driver.switch_to.window(current_handle)
        self._wait()
            
        self._define_element_labels()

        if self.driver.current_url != current_url:
            self.last_page_load_time = time.time() - start
            self._last_input_element = None

    def back(self):
        """Go back to the previous page."""
        self.driver.execute_script("window.history.go(-1)")
        self._wait_for_load()
        self._define_element_labels()

    def hover(self, label : str):
        """
        Hover over element with given label.
        :param label: Element label.
        """
        ac = ActionChains(self.driver)
        ac.move_to_element(self._get_element(label))
        ac.perform()     

    def input(self, label : str, text : str):
        """
        Input given text on element with given label.
        :param label: Element label.
        :param text: Text to add to input element.
        """
        element = self._get_element(label)
        ActionChains(self.driver).click(element).key_down(Keys.LEFT_CONTROL).send_keys("a").key_up(Keys.LEFT_CONTROL).key_down(Keys.DELETE).key_up(Keys.DELETE).perform()
        element.send_keys(text)
        self._last_input_element = element

    def submit(self) -> bool:
        """
        Submit the form for the last input element interacted with.
        """
        if self._last_input_element:
            start = time.time()
            self._last_input_element.submit()
            self._wait_for_load()
            self._wait()
            self._define_element_labels()
            self.last_page_load_time = time.time() - start
            self._last_input_element = None
            return True
        return False

    def select(self, label : str, option : str):
        """
        Change selection of SELECT element.
        :param label: Element label.
        :param option: The option to select.
        """
        element = self._get_element(label)
        if element.tag_name != "select": raise InvalidElementException("Element '%s' is not a SELECT element." % label)
        select = Select(element)
        select.select_by_visible_text(option)

    def scroll_to(self, x : int, y :int):
        """
        Scroll viewport.
        :param x: The amount to scroll horizontally.
        :param y: The amount to scroll vertically.
        """
        self.driver.execute_script("window.scrollTo(%d, %d)" % (x, y))
        self._wait()
        self._define_element_labels()

    def get_page_size(self):
        """ Get size of current page. """
        return (
            self.driver.execute_script("return document.body.scrollWidth;"),
            self.driver.execute_script("return document.body.scrollHeight;")
        )        

    def get_viewport_size(self):
        """ Get the size of the viewport. """
        return (
            self.driver.execute_script("return window.innerWidth"),
            self.driver.execute_script("return window.innerHeight")
        )

    def get_scroll_position(self):
        """ Get viewport scroll position. """
        return (
            self.driver.execute_script("return window.scrollX"),
            self.driver.execute_script("return window.scrollY")
        )

    def screenshot(self, add_element_labels : bool = True) -> str:
        """
        Take a screenshot of current viewport with every interactable
        element labeled in base64 data uri format.
        """

        screenshot = self.driver.get_screenshot_as_png()

        # prepare labels
        if add_element_labels:

            # convert screenshot to byte io
            screenshotRead = io.BytesIO()
            screenshotRead.write(screenshot)
            screenshotRead.seek(0)

            # draw labels
            img = Image.open(screenshotRead).convert("RGB")
            font = ImageFont.load_default(14)
            draw = ImageDraw.Draw(img, mode="RGBA")
            offsetX = self.driver.execute_script("return document.documentElement.scrollLeft")
            offsetY = self.driver.execute_script("return document.documentElement.scrollTop")

            try:
                for element_id, element in self.element_labels.items():
                    x, y = element.location["x"]-5-offsetX, element.location["y"]-3-offsetY
                    draw.rectangle([x-3,y-3,x+22,y+20], fill=(255,255,255,160), outline=(0,0,0,160))
                    draw.text((x, y), element_id, fill=(0,0,0,180), font=font)
            except StaleElementReferenceException:
                self._wait()
                self._define_element_labels()
                return self.screenshot(add_element_labels)

            # write screenshot with labels to byte io
            screenshotWrite = io.BytesIO()
            img.save(screenshotWrite, format="png")
            screenshotWrite.seek(0)
            screenshot = screenshotWrite.read()

        # convert to data uri        
        return "data:image/png;base64," + base64.b64encode(screenshot).decode()

    def close(self):
        """ Close the browser. """
        self.driver.quit()

    def get_secrets_for_url(self, url : str) -> Iterable[Secret]:
        """ Get secrets that match the url. """
        return filter(lambda s: fnmatch(url, s.url_pattern), self.secrets)

    def get_secrets_for_current_url(self) -> Iterable[Secret]:
        """ Get secrets that match the current url. """
        return self.get_secrets_for_url(self.get_current_url())

    def _add_basic_auth_to_url(self, url : str, username : str, password : str) -> str:
        purl = urlparse(url)
        url = url[len(purl.scheme + "://"):]
        creds = "%s:%s" % (quote_plus(username), quote_plus(password))
        return "%s://%s@%s" % (purl.scheme, creds, url)