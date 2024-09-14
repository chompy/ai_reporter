import logging
import gitlab
import tempfile
import zipfile
from typing import Optional

from ....utils import dict_get_type
from .zip import ZipFetcher

class GitlabFetcher(ZipFetcher):

    def __init__(self, key : str = "", config : dict = {}, logger : Optional[logging.Logger] = None):
        super().__init__(key, config, logger)

    def __del__(self):
        super().__del__()
        if self.file: self.file.close()

    @staticmethod
    def name() -> str:
        return "gitlab"

    def load(self):
        if self.logger:
            self.logger.info("Download Gitlab repository '%s'." % self.key, 
                extra={"_module": "gitlab", "action": "download", "object": "project '%s'" % self.key})
        # connect to gitlab
        client = gitlab.Gitlab(private_token=dict_get_type(self.config, "access_token", str, source="fetcher.gitlab"))
        project = client.projects.get(self.key)
        # download zip
        self.file = tempfile.TemporaryFile()
        def _handle_chunk(chunk): self.file.write(chunk)
        project.repository_archive(format="zip", streamed=True, action=_handle_chunk)
        self.file.seek(0)
        self.zf = zipfile.ZipFile(self.file)

    @property
    def root_directory(self) -> str:
        if not self.zf: return ""
        return self.zf.filelist[0].filename.strip().strip("/").split("/")[0]