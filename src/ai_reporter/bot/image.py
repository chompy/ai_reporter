# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
from mimetypes import MimeTypes
from typing import IO, Self

import requests


class Image:
    """
    An image to be included with a prompt and processed by the bot (if supported).
    """

    def __init__(self, mime: str = "image/png", contents: bytes | None = None):
        self.mime = mime
        self.contents = contents

    @classmethod
    def from_url(cls, url: str, headers: dict[str, str] | None = None) -> Self:
        """
        Fetch the image from a URL.

        :param url: The URL where the image is located.
        :param headers: Headers to send as part of request.
        """
        with requests.get(url, stream=True, headers=headers, timeout=30) as resp:
            return cls(cls._guess_mime(url), resp.raw.read())

    @classmethod
    def from_file(cls, path: str) -> Self:
        """
        Fetch the image from a local file.

        :param path: The path to the image.
        """
        with open(path, "rb") as f:
            return cls(cls._guess_mime(path), f.read())

    @classmethod
    def from_stream(cls, fp: IO[bytes], mime: str = "image/png") -> Self:
        """
        Fetch the image from a byte stream.

        :param fp: The byte stream containing the image data.
        :param mime: The mime type of the image.
        """
        return cls(mime, fp.read())

    def to_base64(self) -> str | None:
        """
        Convert the image to a base64 data URI.
        """
        if not self.contents:
            return None
        return (f"data:{self.mime};base64,") + base64.b64encode(self.contents).decode()

    @staticmethod
    def _guess_mime(path: str):
        mime = MimeTypes()
        mime_str = mime.guess_type(path)[0]
        if mime_str and mime_str.startswith("image/"):
            return mime_str
        return "image/png"
