# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


class ConfigError(Exception):
    """An error with a configuration parameter."""


class ConfigParameterTypeError(TypeError, ConfigError):
    """Configuration parameter is an unexpected type."""


class ConfigParameterValueError(ValueError, ConfigError):
    """Configuration parameter is invalid."""
