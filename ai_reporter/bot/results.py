from typing import Optional
from .token_count import TokenCount

class BotResults:

    """ The results of a bot report. """

    def __init__(self, values : dict[str,object] = {}, tokens : Optional[TokenCount] = None):
        self.values = values
        self.tokens = tokens

    @property
    def input_tokens(self) -> int:
        return self.tokens.input if self.tokens else 0

    def output_tokens(self) -> int:
        return self.tokens.output if self.tokens else 0