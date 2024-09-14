from abc import abstractmethod
import logging
from typing import Optional
from .response import ToolResponse

class BaseTool:

    def __init__(self, logger : Optional[logging.Logger] = None, **kwargs):
        self.args = kwargs
        self.logger = logger

    @staticmethod
    @abstractmethod
    def name() -> str:
        """ Name of the tool. """
        return "base"

    @classmethod
    def definition(cls, *args, **kwargs) -> dict:
        """ Properties for the function call. """
        return {
            "name": cls.name()
        }

    @abstractmethod
    def execute(self, **kwargs) -> ToolResponse:
        self._check_properties(kwargs)
        return ToolResponse()

    def _check_properties(self, properties : dict):
        required_properties = self.__class__.definition(**self.args).get("parameters", {}).get("required", [])
        defined_properties = self.__class__.definition(**self.args).get("parameters", {}).get("properties", {})
        for prop_name, _ in defined_properties.items():
            if prop_name in required_properties and prop_name not in properties:
                raise AttributeError("'%s' is required" % prop_name)
            # TODO type checking?        
