from typing import Optional
import logging

from .base import BaseFetcher
from .zip import ZipFetcher
from .gitlab import GitlabFetcher
from ....utils import dict_get_type

AVAILABLE_FETCHERS = [ZipFetcher, GitlabFetcher]

def get_fetcher(name : str, key : str, fetcher_config : dict = {}, logger : Optional[logging.Logger] = None) -> BaseFetcher:
    for fetcher in AVAILABLE_FETCHERS:
        if fetcher.name() == name:
            config = dict_get_type(fetcher_config, name, dict, {}, "tools.code.fetcher")
            return fetcher(key, config, logger)
    raise ValueError("'%s' fetcher is not defined" % name)