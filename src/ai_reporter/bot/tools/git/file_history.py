from ...property import PropertyDefinition
from ..response import ToolMessageResponse
from .base import BaseGitTool

MAX_FILE_SIZE = 131072 # 128KB

class GitFileHistoryTool(BaseGitTool):

    @staticmethod
    def name() -> str:
        return "git-file-history"

    @staticmethod
    def description():
        return "Show the commit history of a file in the repository."

    @staticmethod
    def properties():
        return BaseGitTool.properties() + [
            PropertyDefinition("file", description="The file to view the history of.", required=True)
        ]

    def execute(self, repository : str, file : str, *args, **kwargs):
        super().execute(repository=repository, **kwargs)
        out = ""
        for commit in self.repo.iter_commits(paths=file):
            out += self._display_commit(commit) + "\n"
        out = out.strip()
        return ToolMessageResponse(out if out else "(no commits found)")    
