from ...response import ToolMessageResponse
from .base import BaseWebTool

class WebSubmitTool(BaseWebTool):

    @staticmethod
    def name() -> str:
        return "web-submit"

    @staticmethod
    def description(**kwargs):
        return "Submit the current form in the web browser."

    @staticmethod
    def properties(**kwargs):
        return  []

    def execute(self, *args, **kwargs):
        success = self.browser.submit()
        return ToolMessageResponse(
            self._get_browser_window_info_text(
                "(success)" if success else "(warning: no form was found)"
            ), [self._screenshot()]
        )
