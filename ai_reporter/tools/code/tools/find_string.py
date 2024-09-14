from ...response import ToolResponse
from .base import BaseCodeTool

class FindStringTool(BaseCodeTool):

    ALLOWED_FILE_TYPES = [
        "php", "txt", "py", "go", "yaml", "yml", "md", "twig", "html", "htm", "css", "scss", "sass", "dist",
        "json", "js", "ts", "jsx", "lua", "xml", "sql", "sh", "Dockerfile"
    ]

    @staticmethod
    def name() -> str:
        return "find_string"

    @classmethod
    def definition(cls, **kwargs) -> dict:
        return {
            "name": cls.name(),
            "description": "Search the entire code base for files containing a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "The string to search for."
                    }
                },
                "required": ["search"]
            }
        }

    def execute(self, **kwargs):
        super(FindStringTool, self).execute(**kwargs)
        search = kwargs.get("search", "")
        out = ""
        for path in self.fetcher.file_list():
            allowed_file = False
            for ext in FindStringTool.ALLOWED_FILE_TYPES:
                if path.strip().lower().endswith(ext):
                    allowed_file = True
            if not allowed_file: continue
            with self.fetcher.open(path) as f:
                line_no = 0
                try:
                    contents = f.read().decode("utf-8").strip()
                except:
                    continue
                for line in contents.splitlines():
                    line_no += 1
                    if search in line:
                        out += "%s (line %d)\n" % (path, line_no)
        if not out: return ToolResponse("(no results found)")
        return ToolResponse(self._santitize_output(out.strip()))
