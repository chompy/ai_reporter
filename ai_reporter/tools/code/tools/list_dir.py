import os

from ...response import ToolResponse
from .base import BaseCodeTool

class ListDirTool(BaseCodeTool):

    @staticmethod
    def name() -> str:
        return "list_dir"

    @classmethod
    def definition(cls, **kwargs) -> dict:
        return {
            "name": cls.name(),
            "description": "List all files and directories in a given directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the folder to list (default: project root directory)."
                    }
                }
            }
        }

    def execute(self, **kwargs):
        super(ListDirTool, self).execute(**kwargs)
        path = self._santitize_path(kwargs.get("path", "/"))
        if not path: path = "/"
        output = ""
        for fetcher_path in self.fetcher.dir_list():
            if os.path.dirname(fetcher_path) == path:
                output += "DIR\t%s\n" % fetcher_path
        for fetcher_path in self.fetcher.file_list():
            if os.path.dirname(fetcher_path) == path:
                output += "FILE\t%s\n" % fetcher_path
        if not output: return ToolResponse("(no results found)")
        return ToolResponse(self._santitize_output(output))
