from datetime import datetime, timezone
from itertools import islice
from ...property import PropertyDefinition
from ..response import ToolMessageResponse
from .base import BaseGitTool

LIMIT = 50

class GitListCommitsTool(BaseGitTool):

    @staticmethod
    def name() -> str:
        return "git-list-commits"

    @staticmethod
    def description():
        return "List %d commits in the repository." % LIMIT

    @staticmethod
    def properties():
        return BaseGitTool.properties() + [
            PropertyDefinition("until", description="If provided, list first %d commits that occured before the date, otherwise list most recent commits. Format: YYYY-MM-DD" % LIMIT)
        ]

    def execute(self, repository : str, until : str = "", *args, **kwargs):
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
