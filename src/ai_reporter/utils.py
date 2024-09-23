from typing import Any, Optional, TypeVar

from .error.config import ConfigParameterTypeError

T = TypeVar("T")

def check_type(value : Any, expected_type : type, name : Optional[str] = None, error : type[Exception] = TypeError):
    if isinstance(value, expected_type): return
    actual_type_name = str(value.__class__.__name__ if isinstance(value, expected_type) else type(value))
    if name: raise error("unexpected type for '%s', expected %s but got %s" % (name, str(expected_type), actual_type_name))
    raise error("unexpected type, expected %s but got %s" % (str(expected_type), actual_type_name))

def check_config_type(value : Any, expected_type : type, name : Optional[str] = None):
    check_type(value, expected_type, name, ConfigParameterTypeError)