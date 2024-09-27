# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

import contextlib
import os
from string import Template

from git import Commit, GitCommandError, ODBError, Repo

from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.base import BaseTool
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.error.bot import ToolPropertyInvalidError

COMMIT_TEMPLATE = """
COMMIT: $id
BY: $author
DATE: $date
MESSAGE: $message
"""


class BaseGitTool(BaseTool):
    def execute(self, repository: str):
        self.repo = self._open_repo(repository)
        return ToolMessageResponse("(none)")

    def properties(self):
        return [PropertyDefinition("repository", description="The Git repository to use.", required=True)]

    def _open_repo(self, repo: str) -> Repo:
        if "repo_name" in self.state and self.state["repo_name"] == repo and isinstance(self.state["repo"], Repo):
            return self.state["repo"]
        repo_name = os.path.basename(repo)
        path_to = os.path.join(self.work_path, repo_name)
        if os.path.exists(path_to):
            self.state["repo"] = Repo.init(path_to)
            with contextlib.suppress(ODBError):
                self.state["repo"].remotes[0].pull()
            return self.state["repo"]
        try:
            return Repo.clone_from(repo, path_to)
        except GitCommandError as e:
            self._log_error(f"Git error when cloning '{repo}'.", e, {"git_repository": repo})
            # TODO: is there a way to determine if this is a bot error or a user configuration error?
            raise ToolPropertyInvalidError(self.name(), "repository") from e

    def _display_commit(self, commit: Commit) -> str:
        return Template(COMMIT_TEMPLATE.strip()).substitute(
            {
                "id": commit.hexsha,
                "author": commit.author,
                "date": commit.authored_datetime.strftime("%Y-%m-%d"),
                "message": commit.message,
            }
        )
