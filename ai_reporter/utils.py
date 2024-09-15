from typing import Optional, TypeVar

T = TypeVar("T")

def dict_get_type(data : dict, key : str, expected_type : type[T], default : Optional[T] = None, source : str = "") -> T:
    value = data.copy()
    for k in key.split("."):
        if type(value) is not dict or k not in value: 
            if default: return default
            raise ValueError("value not defined at key '%s%s'" % ((("%s:" % source) if source else ""), key))
        value = value.get(k, {})
    if isinstance(value, expected_type): return value
    raise TypeError("unexpected type at key '%s%s', expected %s but got %s" % (key, "%s:" if source else "", expected_type, type(value)))

def dict_get_type_none(data : dict, key : str, expected_type : type[T], default : Optional[T] = None, source : str = "") -> Optional[T]:
    try: return dict_get_type(data, key, expected_type, default, source)
    except ValueError: return default

def get_property_type_name(key : str, properties : dict) -> str:
    out = properties.get("_%s_type" % key)
    if out: return out
    if key.startswith("has_") or key.startswith("is_"): return "boolean"
    return "string"
