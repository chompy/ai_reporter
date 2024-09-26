# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_reporter.bot.token_count import TokenCount


class BotResults:
    """The results of a bot report."""

    def __init__(self, values: dict[str, object] | None = None, tokens: TokenCount | None = None):
        self.values = values if values else {}
        self.tokens = tokens

    @property
    def input_tokens(self) -> int:
        return self.tokens.input if self.tokens else 0

    def output_tokens(self) -> int:
        return self.tokens.output if self.tokens else 0
