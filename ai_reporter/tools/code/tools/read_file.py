from ...response import ToolMessageResponse
from .base import BaseCodeTool

class ReadFileTool(BaseCodeTool):

    @staticmethod
    def name():
        return "read_file"

    @classmethod
    def definition(cls, **kwargs):
        return {
            "name": cls.name(),
            "description": "Read the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the file to read."
                    }
                },
                "required": ["path"]
            }
        }

    def execute(self, **kwargs):
        super(ReadFileTool, self).execute(**kwargs)
        path = self._santitize_path(kwargs.get("path", ""))
        try:
            with self.fetcher.open(path) as fp:
                lines = fp.read().decode("utf-8").splitlines()
            output = ""
            for i in range(len(lines)):
                output += "%s\n" % (lines[i])
        except KeyError:
            return ToolMessageResponse("(file not found)")
        return ToolMessageResponse(self._santitize_output(output))
