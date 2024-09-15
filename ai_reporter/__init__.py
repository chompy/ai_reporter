import logging
from typing import Optional

from .bot.client import BotClient
from .input.prompt import Prompt

def run_report(prompt : Prompt, config : dict = {}, logger : Optional[logging.Logger] = None) -> dict[str,object]:
    bot = BotClient(logger=logger, **config)
    return bot.run(prompt)