from abc import abstractmethod
import contextlib
import logging
from typing import IO, Iterable, Iterator, Optional

class BaseFetcher:

    def __init__(self, key : str = "", config : dict = {}, logger : Optional[logging.Logger] = None):
        self.key = key
        self.config = config
        self.logger = logger

    @staticmethod
    @abstractmethod
    def name() -> str: ...

    @abstractmethod
    @contextlib.contextmanager
    def open(self, path : str) -> Iterator[IO[bytes]]: ...

    @abstractmethod
    def dir_list(self) -> Iterable[str]: ...

    @abstractmethod
    def file_list(self) -> Iterable[str]: ...