import contextlib
import logging
import os
from typing import IO, Iterator, Optional
import zipfile

from .base import BaseFetcher

class ZipFetcher(BaseFetcher):

    def __init__(self, key : str = "", config : dict = {}, logger : Optional[logging.Logger] = None):
        super().__init__(key, config, logger)
        self.load()

    def __del__(self):
        if self.zf: self.zf.close()

    @staticmethod
    def name() -> str:
        return "zip"

    def load(self):
        self.zf = zipfile.ZipFile(self.key)

    @property
    def root_directory(self) -> str:
        return "/"

    @contextlib.contextmanager
    def open(self, path : str) -> Iterator[IO[bytes]]:
        inner_zip_path = os.path.join(self.root_directory, path.strip("/"))
        fp = self.zf.open(inner_zip_path, "r")
        try:
            yield fp
        finally:
            fp.close()

    def dir_list(self) -> Iterator[str]:
        for f in self.zf.filelist:
            if f.is_dir():
                path = "/" + ("/".join(f.filename.split("/")[1:])).strip("/")
                if path == "/": continue
                yield path

    def file_list(self) -> Iterator[str]:
        for f in self.zf.filelist:
            if not f.is_dir():
                path = "/" + ("/".join(f.filename.split("/")[1:])).strip("/")
                if path == "/": continue
                yield path
