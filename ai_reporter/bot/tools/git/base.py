import os
from string import Template

from git import Commit, GitCommandError, Repo

from ....error.bot import ToolPropertyInvalidError
from ...property import PropertyDefinition
from ..base import BaseTool
from ..response import ToolMessageResponse

COMMIT_TEMPLATE = """
COMMIT: $id
BY: $author
DATE: $date
MESSAGE: $message
"""

class BaseGitTool(BaseTool):

    def execute(self, repository : str, **kwargs):
        self.repo = self._open_repo(repository)
        return ToolMessageResponse("(none)")

    @staticmethod
    def properties():
        return [
            PropertyDefinition("repository", description="The Git repository to use.", required=True)
        ]

    def _open_repo(self, repo : str) -> Repo:
        if "repo_name" in self.state and self.state["repo_name"] == repo and isinstance(self.state["repo"], Repo):
            return self.state["repo"]
        repo_name = os.path.basename(repo)
        path_to = os.path.join(self.work_path, repo_name)
        if os.path.exists(path_to):
            self.state["repo"] = Repo.init(path_to)
            try: self.state["repo"].remotes[0].pull()
            except: pass
            return self.state["repo"]
        try:
            return Repo.clone_from(repo, path_to)
        except GitCommandError as e:
            self._log_error("Git error when cloning '%s'." % repo, e, {"repository": repo})
            # TODO is there a way to determine if this is a bot error or a user configuration error?
            raise ToolPropertyInvalidError(self.name(), "repository")

    def _display_commit(self, commit : Commit) -> str:
        return Template(COMMIT_TEMPLATE.strip()).substitute({
            "id": commit.hexsha,
            "author": commit.author,
            "date": commit.authored_datetime.strftime("%Y-%m-%d"),
            "message": commit.message
        })
