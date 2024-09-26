# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from fnmatch import fnmatch

from git import BadName, Blob, Tree

from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.git.base import BaseGitTool
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.error.bot import ToolPropertyInvalidError


class GitSearchFileTool(BaseGitTool):
    @staticmethod
    def name() -> str:
        return "git-search-file"

    @staticmethod
    def description():
        return "Search the the repository for files matching the given name, wildcards are supported."

    @staticmethod
    def properties():
        return [
            *BaseGitTool.properties(),
            PropertyDefinition("name", description="The name to search for.", required=True),
            PropertyDefinition(
                "commit",
                description="The commit to base the search in, use the most recent commit (HEAD) if not provided.",
            ),
        ]

    def execute(self, repository: str, name: str, commit: str = "HEAD", **kwargs):
        super().execute(repository=repository, **kwargs)
        out = ""
        try:
            commit_obj = self.repo.commit(commit)
            out = "\n".join(list(set(self._search_tree(name, commit_obj.tree))))
        except BadName as e:
            self._log_error(
                "Error occured when trying search tree.",
                e,
                {"search_filename": name, "git_repository": repository, "git_commit": commit},
            )
            raise ToolPropertyInvalidError(self.name(), "commit") from e
        return ToolMessageResponse(out if out else "(no files found)")

    def _search_tree(self, name: str, tree: Tree) -> list[str]:
        return [i.path for i in filter(lambda i: isinstance(i, Blob) and fnmatch(i.name, name), tree.traverse())]
