from typing import Self
from enum import StrEnum

from ....utils import dict_get_type

class SecretType(StrEnum):
    HTTP_BASIC = "http"
    FORM = "form"

class Secret:

    def __init__(self, key : str, value : str, type : SecretType = SecretType.FORM, url_pattern : str = "*"):
        self.key = key
        self.value = value
        self.type = type
        self.url_pattern = url_pattern

    @classmethod
    def from_dict(cls, data : dict) -> Self:
        return cls(
            key=dict_get_type(data, "key", str),
            value=dict_get_type(data, "value", str),
            type=SecretType(dict_get_type(data, "type", str)),
            url_pattern=dict_get_type(data, "url_pattern", str)
        )

