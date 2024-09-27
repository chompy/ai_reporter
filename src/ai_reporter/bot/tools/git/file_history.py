# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.git.base import BaseGitTool
from ai_reporter.bot.tools.response import ToolMessageResponse

MAX_FILE_SIZE = 131072  # 128KB


class GitFileHistoryTool(BaseGitTool):
    @staticmethod
    def name() -> str:
        return "git-file-history"

    def description(self):
        return "Show the commit history of a file in the repository."

    def properties(self):
        return [
            *BaseGitTool.properties(),
            PropertyDefinition("file", description="The file to view the history of.", required=True),
        ]

    def execute(self, repository: str, file: str, **kwargs):
        super().execute(repository=repository, **kwargs)
        out = ""
        for commit in self.repo.iter_commits(paths=file):
            out += self._display_commit(commit) + "\n"
        out = out.strip()
        return ToolMessageResponse(out if out else "(no commits found)")
