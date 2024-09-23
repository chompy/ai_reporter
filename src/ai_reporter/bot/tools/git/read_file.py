from git import BadName, Blob, Optional, Tree

from ....error.bot import ToolPropertyInvalidError
from ...property import PropertyDefinition
from ..response import ToolMessageResponse
from .base import BaseGitTool

MAX_FILE_SIZE = 131072 # 128KB

class GitReadFileTool(BaseGitTool):

    @staticmethod
    def name() -> str:
        return "git-read-file"

    @staticmethod
    def description():
        return "Read the contents of a file in the repostory."

    @staticmethod
    def properties():
        return BaseGitTool.properties() + [
            PropertyDefinition("file", description="The file to read.", required=True),
            PropertyDefinition("commit", 
                description="The commit to base the search in, use the most recent commit (HEAD) if not provided."),
        ]

    def execute(self, repository : str, file : str, commit : str = "HEAD", *args, **kwargs):
        super().execute(repository=repository, **kwargs)
        out = ""
        try:
            commit_obj = self.repo.commit(commit)
            out = self._search_tree(file, commit_obj.tree)
        except BadName as e:
            self._log_error("Error occured trying to read file.", e, {"git_repository": repository, "git_file": file, "git_commit": commit})
            raise ToolPropertyInvalidError(self.name(), "commit")
        return ToolMessageResponse(out if out else "(file not found)")

    def _search_tree(self, file : str, tree : Tree) -> Optional[str]:
        for item in tree.traverse():
            if isinstance(item, Blob):
                if item.path == file.lstrip("/"):
                    return bytes(item.data_stream.read()).decode("utf-8")
        return None


