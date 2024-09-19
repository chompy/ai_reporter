from git import BadName, Blob, Tree

from ....error.bot import ToolPropertyInvalidError
from ...property import PropertyDefinition
from ..response import ToolMessageResponse
from .base import BaseGitTool

MAX_FILE_SIZE = 131072 # 128KB

class GitSearchStringTool(BaseGitTool):

    @staticmethod
    def name() -> str:
        return "git-search-string"

    @staticmethod
    def description():
        return "Search the the repository for files containing a string."

    @staticmethod
    def properties():
        return BaseGitTool.properties() + [
            PropertyDefinition("string", description="The string to search for.", required=True),
            PropertyDefinition("commit", 
                description="The commit to base the search in, use the most recent commit (HEAD) if not provided."),
        ]

    def execute(self, repository : str, string : str, commit : str = "HEAD", *args, **kwargs):
        super().execute(repository=repository, **kwargs)
        out = ""
        try:
            commit_obj = self.repo.commit(commit)
            out = "\n".join(list(set(self._search_tree(string, commit_obj.tree))))
        except BadName:
            raise ToolPropertyInvalidError(self.name(), "commit")
        return ToolMessageResponse(out if out else "(no files found)")

    def _search_tree(self, string : str, tree : Tree) -> list[str]:
        out = []
        for item in tree.traverse():
            if isinstance(item, Blob):
                if item.size > MAX_FILE_SIZE: continue
                data = bytes(item.data_stream.read()).decode("utf-8")
                if string in data: out.append(item.path)
        return out