import logging
from typing import Optional

from ...base import BaseTool
from ..fetcher import BaseFetcher

MAX_OUTPUT_SIZE = 32768
LINE_TRUNCATE_LENGTH = 1024

class BaseCodeTool(BaseTool):

    def __init__(self, fetcher : BaseFetcher, max_iterations : int = 10, max_error_retry : int = 3, logger : Optional[logging.Logger] = None, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.fetcher = fetcher
        self.max_iterations = max_iterations
        self.max_error_retry = max_error_retry

    def _santitize_path(self, path : str) -> str:
        original_path = path.split("/")
        fixed_path = []
        for d in original_path:
            if d == "..":
                if len(fixed_path) > 0: fixed_path.pop()
            elif d == "." or not d: continue
            else: fixed_path.append(d)
        return "/" + ("/".join(list(filter(None, fixed_path)))).strip("/")

    def _santitize_output(self, output : str) -> str:
        output_lines = output.splitlines()
        current_size = 0
        for i in range(len(output_lines)):
            if len(output_lines[i]) > LINE_TRUNCATE_LENGTH:
                output_lines[i] = output_lines[i][0:LINE_TRUNCATE_LENGTH] + "...TRUNCATED"
            current_size += len(output_lines[i])
            if current_size > MAX_OUTPUT_SIZE:
                return "\n".join(output_lines[0:i]) + "\n...FILE TRUNCATED..."
        return "\n".join(output_lines)