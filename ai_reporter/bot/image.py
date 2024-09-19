import requests
import base64
from mimetypes import MimeTypes

from typing import Self, Optional, IO

class Image:

    """ An image to be included with a prompt. """

    def __init__(self):
        self.mime = "image/png"
        self.contents : Optional[bytes] = None

    @classmethod
    def from_url(cls, url : str, headers : dict[str,str] = {}) -> Self:
        out = cls()
        # determine mine
        mime = MimeTypes()
        out.mime = mime.guess_type(url)[0]
        if not out.mime or not out.mime.startswith("image/"): out.mime = "image/png"
        # fetch from remote
        resp = requests.get(url, stream=True, headers=headers)
        out.contents = resp.raw.read()
        return out

    @classmethod
    def from_file(cls, path : str) -> Self:
        out = cls()
        # determine mine
        mime = MimeTypes()
        out.mime = mime.guess_type(path)[0]
        if not out.mime or not out.mime.startswith("image/"): out.mime = "image/png"
        # fetch from file system
        with open(path, "rb") as f:
            out.contents = f.read()
        return out

    @classmethod
    def from_stream(cls, fp : IO[bytes], mime : str = "image/png") -> Self:
        out = cls()
        out.mime = mime
        out.contents = fp.read()
        return out

    def to_base64(self) -> Optional[str]:
        if not self.contents: return None
        return ("data:%s;base64," % (self.mime)) + base64.b64encode(self.contents).decode()