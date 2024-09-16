from enum import StrEnum

class SecretType(StrEnum):
    HTTP_BASIC = "http"
    FORM = "form"

class Secret:

    def __init__(self, key : str, value : str, type : SecretType = SecretType.FORM, url_pattern : str = "*"):
        self.key = key
        self.value = value
        self.type = type
        self.url_pattern = url_pattern