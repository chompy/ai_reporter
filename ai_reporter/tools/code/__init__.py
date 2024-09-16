import logging
from typing import Iterable, Optional

from ...error.bot import ToolPropertyInvalidError
from ...utils import dict_get_type
from ..base import BaseTool
from ..response import ToolPromptResponse
from .fetcher import get_fetcher
from .tools import AVAILABLE_TOOLS

DEFAULT_SYSTEM_PROMPT = """
Adopt the role of a quality assurance (QA) engineer.
You will be asked to perform an analysis of a code base. You have access to tools that will allow you the examine the code base. Perform the task in as few steps as possible. When you have reached a conclusion use the `done` tool to finish.
"""

class CodeTool(BaseTool):

    def __init__(
        self, 
        code_bases : Iterable[str],
        system_prompt : Optional[str] = None,
        max_iterations : Optional[int] = None,
        max_error_retries : Optional[int] = None,
        logger : Optional[logging.Logger] = None,
        **kwargs
    ):
        super().__init__(logger=logger)
        self.args = {"code_bases": code_bases, **kwargs}
        self.code_bases = code_bases
        self.max_iterations = max_iterations
        self.max_error_retries = max_error_retries
        self.system_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT

    @staticmethod
    def name() -> str:
        return "code"

    @classmethod
    def definition(cls, code_bases : Iterable[str], **kwargs) -> dict:
        return {
            "name": cls.name(),
            "description": "Ask a large language model to examine a code base and report on its findings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code_base": {
                        "type": "string",
                        "description": "The code base to examine.",
                        "enum": list(code_bases)
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Prompt for the large language model."
                    }
                },
                "required": ["repository", "prompt"]
            }
        }


    def execute(self, **kwargs):
        super(self.__class__, self).execute(**kwargs)

        # ensure code base bot provides is defined
        code_base = dict_get_type(kwargs, "code_base", str)
        if code_base not in self.code_bases: raise ToolPropertyInvalidError(self.name(), "code_base")

        # find fetcher for code base
        fetcher_name, key = code_base.split(":")
        fetcher = get_fetcher(fetcher_name, key, self.args, self.logger)

        # build prompt for code bot
        return ToolPromptResponse(
            user_prompt=dict_get_type(kwargs, "prompt", str),
            system_prompt=self.system_prompt,
            max_iterations=self.max_iterations if self.max_iterations else 15,
            max_error_retry=self.max_error_retries if self.max_error_retries else 3,
            tools=dict(map(lambda t: (t.name(), {"fetcher": fetcher}), AVAILABLE_TOOLS))
        )