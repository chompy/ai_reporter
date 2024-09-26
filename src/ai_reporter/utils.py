# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, TypeVar

from ai_reporter.error.config import ConfigParameterTypeError

T = TypeVar("T")


def check_type(value: Any, expected_type: type, name: str | None = None, error: type[Exception] = TypeError):
    if isinstance(value, expected_type):
        return
    actual_type_name = str(value.__class__.__name__ if isinstance(value, expected_type) else type(value))
    msg = f"unexpected type, expected {expected_type!s} but got {actual_type_name}"
    if name:
        msg = f"unexpected type for '{name}', expected {expected_type!s} but got {actual_type_name}"
    raise error(msg)


def check_config_type(value: Any, expected_type: type, name: str | None = None):
    check_type(value, expected_type, name, ConfigParameterTypeError)
