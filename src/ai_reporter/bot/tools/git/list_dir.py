from git import BadName, Blob, Tree

from ....error.bot import ToolPropertyInvalidError
from ...property import PropertyDefinition
from ..response import ToolMessageResponse
from .base import BaseGitTool

class GitListDirTool(BaseGitTool):

    @staticmethod
    def name() -> str:
        return "git-list-dir"

    @staticmethod
    def description():
        return "List all files for a given directory in the repository."

    @staticmethod
    def properties():
        return BaseGitTool.properties() + [
            PropertyDefinition("path", description="The path of the directory to list, use the root directory if not provided."),
            PropertyDefinition("commit", 
                description="The commit to base the search in, use the most recent commit (HEAD) if not provided."),
        ]

    def execute(self, repository : str, path : str = "", commit : str = "HEAD", *args, **kwargs):
        super().execute(repository=repository, **kwargs)
        try:
            commit_obj = self.repo.commit(commit)
            dir_list = self._search_tree(path, commit_obj.tree)
            return ToolMessageResponse(
                "\n".join(list(set(dir_list))) if dir_list else "(empty directory)"
            )
        except BadName as e:
            self._log_error("Error occured trying to list directory.", e, {"git_repository": repository, "git_path": path, "git_commit": commit})
            raise ToolPropertyInvalidError(self.name(), "commit")

    def _search_tree(self, path : str, tree : Tree) -> list[str]:
        out = []
        for item in tree.traverse():
            if isinstance(item, Tree) or isinstance(item, Blob):
                if item.path == (path.strip("/") + "/" + item.name).lstrip("/"): out.append(item.path)
        return out
