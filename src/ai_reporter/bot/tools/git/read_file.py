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


class GitReadFileTool(BaseGitTool):
    @staticmethod
    def name() -> str:
        return "git-read-file"

    def description(self):
        return "Read the contents of a file in the repostory."

    def properties(self):
        return [
            *BaseGitTool.properties(),
            PropertyDefinition("file", description="The file to read.", required=True),
            PropertyDefinition(
                "commit",
                description="The commit to base the search in, use the most recent commit (HEAD) if not provided.",
            ),
        ]

    def execute(self, repository: str, file: str, commit: str = "HEAD", **kwargs):
        super().execute(repository=repository, **kwargs)
        out = ""
        try:
            commit_obj = self.repo.commit(commit)
            out = self._search_tree(file, commit_obj.tree)
        except BadName as e:
            self._log_error(
                "Error occured trying to read file.",
                e,
                {"git_repository": repository, "git_file": file, "git_commit": commit},
            )
            raise ToolPropertyInvalidError(self.name(), "commit") from e
        return ToolMessageResponse(out if out else "(file not found)")

    def _search_tree(self, file: str, tree: Tree) -> str | None:
        return next(filter(lambda i: isinstance(i, Blob) and i.path == file.lstrip("/"), tree.traverse), None)
