# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from datetime import datetime, timezone
from itertools import islice

from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.git.base import BaseGitTool
from ai_reporter.bot.tools.response import ToolMessageResponse

LIMIT = 50


class GitListCommitsTool(BaseGitTool):
    @staticmethod
    def name() -> str:
        return "git-list-commits"

    def description(self):
        return "List %d commits in the repository." % LIMIT

    def properties(self):
        return [
            *BaseGitTool.properties(),
            PropertyDefinition(
                "until",
                description="If provided, list first %d commits that occured before the date, otherwise list most recent commits. Format: YYYY-MM-DD"
                % LIMIT,
            ),
        ]

    def execute(self, repository: str, until: str = "", **kwargs):
        super().execute(repository=repository, **kwargs)
        out = ""
        commits = self.repo.iter_commits()
        if until:
            until_dt = datetime.strptime(until, "%Y-%m-%d").astimezone(timezone.utc)
            commits = filter(lambda c: c.authored_datetime <= until_dt, commits)
        for commit in islice(commits, LIMIT):
            out += self._display_commit(commit) + "\n"
        out = out.strip()
        return ToolMessageResponse(out if out else "(no commits found)")
