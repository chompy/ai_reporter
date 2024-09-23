from enum import StrEnum

from ....utils import check_config_type

class SecretType(StrEnum):
    HTTP_BASIC = "http"
    FORM = "form"

class Secret:

    """ A secret value for use with the web browser either HTTP basic auth credientials or a username/password for a login form. """

    def __init__(self, key : str, value : str, type : SecretType = SecretType.FORM, url_pattern : str = "*"):
        check_config_type(key, str, "tools.web.secrets.[].key")
        check_config_type(value, str, "tools.web.secrets.[].value")
        check_config_type(type, str, "tools.web.secrets.[].type")
        check_config_type(url_pattern, str, "tools.web.secrets.[].url_pattern")
        self.key = key
        self.value = value
        self.type = type
        self.url_pattern = url_pattern