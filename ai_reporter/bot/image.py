import base64
from mimetypes import MimeTypes
from typing import IO, Optional, Self

import requests

class Image:

    """ An image to be included with a prompt and processed by bot (if supported). """

    def __init__(self, mime : str = "image/png", contents : Optional[bytes] = None):
        self.mime = mime
        self.contents = contents

    @classmethod
    def from_url(cls, url : str, headers : dict[str,str] = {}) -> Self:
        with requests.get(url, stream=True, headers=headers) as resp:
            return cls(cls._guess_mime(url), resp.raw.read())

    @classmethod
    def from_file(cls, path : str) -> Self:
        with open(path, "rb") as f:
            return cls(cls._guess_mime(path), f.read())

    @classmethod
    def from_stream(cls, fp : IO[bytes], mime : str = "image/png") -> Self:
        return cls(mime, fp.read())

    def to_base64(self) -> Optional[str]:
        if not self.contents: return None
        return ("data:%s;base64," % (self.mime)) + base64.b64encode(self.contents).decode()

    @staticmethod    
    def _guess_mime(path : str):
        mime = MimeTypes()
        mime_str = mime.guess_type(path)[0]
        if mime_str and mime_str.startswith("image/"): return mime_str
        return "image/png"