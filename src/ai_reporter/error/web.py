# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


class ElementNotFoundError(Exception):
    """Element was not found."""


class InvalidElementError(Exception):
    """Tried to perform an invalid action on an element."""
