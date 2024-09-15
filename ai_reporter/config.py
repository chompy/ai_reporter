import os
from typing import Optional, Union

import yaml

from .utils import dict_get_type, dict_get_type_none

DEFAULT_CONFIG_PATH = "assets/config_default.yaml"

class Config:
    
    def __init__(self, config_path : str = "config.yaml"):
        self._config : dict[str,object] = {}
        self._reports : dict[str,object] = {}
        self._load(config_path)

    def _load(self, config_path):
        with open(DEFAULT_CONFIG_PATH, "r") as f:
            self._config = yaml.safe_load(f)
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                self._config = {**self._config, **yaml.safe_load(f)}
        with open(self.get_string("pathes.reports", "assets/reports.yaml"), "r") as f:
            self._reports = yaml.safe_load(f)
        return self

    def get(self, key : str, default = None) -> Optional[object]:
        return dict_get_type_none(self._config, key, object, default, "config")

    def get_string(self, key : str, default : str = "") -> str:
        return dict_get_type(self._config, key, str, default, "config")

    def get_int(self, key : str, default : int = 0) -> int:
        return dict_get_type(self._config, key, int, default, "config")

    def get_dict(self, key : str) -> dict:
        return dict_get_type(self._config, key, dict, {}, "config")

    def get_report_type(self, name : str) -> dict[str,object]:
        out = {}
        out.update(dict_get_type(self._reports, "_default", dict, {}))
        out.update(dict_get_type(self._reports, name, dict, {}))
        return out

    def get_all_report_types(self) -> list[dict]:
        out = []
        for name, _ in self._reports.items():
            if not name or name[0] == "_": continue
            out.append(self.get_report_type(name))
        return out

    def get_workflow_configs(self) -> list[dict]:
        return dict_get_type(self._reports, "_workflows", list, [])