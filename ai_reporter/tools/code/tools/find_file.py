import fnmatch

from ...response import ToolMessageResponse
from .base import BaseCodeTool

class FindFileTool(BaseCodeTool):

    @staticmethod
    def name() -> str:
        return "find_file"

    @classmethod
    def definition(cls, **kwargs) -> dict:
        return {
            "name": cls.name(),
            "description": "Search recursively from the code base root directory for a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of file to search for, wildcards are supported."
                    }
                },
                "required": ["name"]
            }
        }

    def execute(self, **kwargs):
        super(FindFileTool, self).execute(**kwargs)
        name = kwargs.get("name", "").lstrip("/")
        matched_files = list(filter(lambda f: fnmatch.fnmatch(f, "*/" + name), self.fetcher.file_list()))
        if matched_files:
            return ToolMessageResponse("\n".join(matched_files))
        return ToolMessageResponse("(no files found)")