# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from git import BadName, Blob, Tree

from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.git.base import BaseGitTool
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.error.bot import ToolPropertyInvalidError

MAX_FILE_SIZE = 131072  # 128KB


class GitSearchStringTool(BaseGitTool):
    @staticmethod
    def name() -> str:
        return "git-search-string"

    @staticmethod
    def description():
        return "Search the the repository for files containing a string."

    @staticmethod
    def properties():
        return [
            *BaseGitTool.properties(),
            PropertyDefinition("string", description="The string to search for.", required=True),
            PropertyDefinition(
                "commit",
                description="The commit to base the search in, use the most recent commit (HEAD) if not provided.",
            ),
        ]

    def execute(self, repository: str, string: str, commit: str = "HEAD", **kwargs):
        super().execute(repository=repository, **kwargs)
        out = ""
        try:
            commit_obj = self.repo.commit(commit)
            out = "\n".join(list(set(self._search_tree(string, commit_obj.tree))))
        except BadName as e:
            self._log_error(
                "Error occured when trying search tree.",
                e,
                {"search_string": string, "git_repository": repository, "git_commit": commit},
            )
            raise ToolPropertyInvalidError(self.name(), "commit") from e
        return ToolMessageResponse(out if out else "(no files found)")

    def _search_tree(self, string: str, tree: Tree) -> list[str]:
        out = []
        for item in tree.traverse():
            if isinstance(item, Blob):
                if item.size > MAX_FILE_SIZE:
                    continue
                data = bytes(item.data_stream.read()).decode("utf-8")
                if string in data:
                    out.append(item.path)
        return out
