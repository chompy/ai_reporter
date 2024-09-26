# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from ai_reporter.bot.client.null_client import NullClient
from ai_reporter.bot.client.openai_client import OpenAIClient
from ai_reporter.error.bot import BotClientNotExistError

if TYPE_CHECKING:
    from logging import Logger

    from ai_reporter.bot.client.base_client import BaseClient

BOT_CLIENTS = [OpenAIClient, NullClient]


def get_bot_client(name: str, config: dict, logger: Logger | None = None) -> BaseClient:
    """
    Retrieve a bot client by its name and configuration.

    :param name: The bot client name.
    :param config: The bot client configuration.
    :param logger: Optional logger.
    """
    for client in BOT_CLIENTS:
        if client.name() == name:
            return client(logger=logger, **config)
    msg = f"bot client '{name}' does not exist"
    raise BotClientNotExistError(msg)
