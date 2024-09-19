from typing import Optional
import logging
from .base_client import BaseClient
from .openai_client import OpenAIClient
from ...error.bot import BotClientNotExistError

BOT_CLIENTS = [OpenAIClient]

def get_bot_client(name : str, config : dict, logger : Optional[logging.Logger] = None) -> BaseClient:
    for client in BOT_CLIENTS:
        if client.name() == name:
            return client(logger=logger, **config)
    raise BotClientNotExistError("bot client '%s' does not exist" % name)