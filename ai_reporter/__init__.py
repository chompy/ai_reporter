import logging
from typing import Optional

from .bot import BotResults, Prompt, get_bot_client

def run_report(prompt : Prompt, config : dict = {}, logger : Optional[logging.Logger] = None) -> BotResults:
    return get_bot_client(config.get("bot_client", "openai"), config, logger).run(prompt)