from fnmatch import fnmatch

from git import BadName, Tree, Blob

from ....error.bot import ToolPropertyInvalidError
from ...property import PropertyDefinition
from ..response import ToolMessageResponse
from .base import BaseGitTool

class GitSearchFileTool(BaseGitTool):

    @staticmethod
    def name() -> str:
        return "git-search-file"

    @staticmethod
    def description():
        return "Search the the repository for files matching the given name, wildcards are supported."

    @staticmethod
    def properties():
        return BaseGitTool.properties() + [
            PropertyDefinition("name", description="The name to search for.", required=True),
            PropertyDefinition("commit", 
                description="The commit to base the search in, use the most recent commit (HEAD) if not provided."),
        ]

    def execute(self, repository : str, name : str, commit : str = "HEAD", *args, **kwargs):
        super().execute(repository=repository, **kwargs)
        out = ""
        try:
            commit_obj = self.repo.commit(commit)
            out = "\n".join(list(set(self._search_tree(name, commit_obj.tree))))
        except BadName:
            raise ToolPropertyInvalidError(self.name(), "commit")
        return ToolMessageResponse(out if out else "(no files found)")

    def _search_tree(self, name : str, tree : Tree) -> list[str]:
        out = []
        for item in tree.traverse():
            if isinstance(item, Blob) and fnmatch(item.name, name):
                out.append(item.path)
        return out
