from typing import Optional
import logging
from .base_client import BaseClient
from .openai_client import OpenAIClient
from .null_client import NullClient
from ...error.bot import BotClientNotExistError

BOT_CLIENTS = [OpenAIClient, NullClient]

def get_bot_client(name : str, config : dict, logger : Optional[logging.Logger] = None) -> BaseClient:
    """
    Retrieve a bot client by its name and configuration.

    :param name: The bot client name.
    :param config: The bot client configuration.
    :param logger: Optional logger.
    """
    for client in BOT_CLIENTS:
        if client.name() == name:
            return client(logger=logger, **config)
    raise BotClientNotExistError("bot client '%s' does not exist" % name)