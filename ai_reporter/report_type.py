from typing import Optional, Callable, Self
from .bot.prompt import Prompt

class ReportType:

    """ Defines a type of report. """

    def __init__(self, name : str, prompt : Prompt, next_report_type : Optional[Callable[[dict[str,dict]], Self]] = None):
        """
        :param name: Name of report type.
        :param prompt: The prompt to use when running this report.
        :param next_report_type: Callable that should return the next report type to run. It will be passed a dictionary of report type names with report values.
        """
        self.name = name
        self.prompt = prompt
        self.next_report_type = next_report_type

    def next(self, values : dict[str,dict] = {}) -> Optional[Self]:
        if not self.next_report_type: return None
        return self.next_report_type(values)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "prompt": self.prompt.to_dict(),
            "has_next_report": True if self.next_report_type else False
        }