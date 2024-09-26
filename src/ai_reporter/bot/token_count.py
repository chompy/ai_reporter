# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


class TokenCount:
    """Track the token usage for a report."""

    def __init__(self):
        self.input = 0
        self.output = 0
