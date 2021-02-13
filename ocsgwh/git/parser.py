# -*- coding: utf-8 -*-
# OpenCS Git Work History - A simple Git Report Generator
# Copyright(C) 2021 Open Communications Security
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY
# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see < https: // www.gnu.org/licenses/>.
import re
from datetime import datetime
import subprocess
from pathlib import Path
from .model import *

from logging import getLogger
LOGGER = getLogger(__name__)


def parse_iso_date(s):
    """
    Parses a strict ISO date (e.g.: '2021-01-21T14:24:07-03:00').
    """
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S%z')


# This is the Git log command that will be parsed by this application.
# It will generate a log of all commits in the repository, regardless of
# the branches. Each log will have the following format:
#
# ```
# *****
# <Commit Hash>
# <Parent Hash> [<Parent Hash>]
# <Author Name>
# <Author email>
# <Author date using strict ISO format>
#
# <added>\t<deleted>\t<file name>
#
# ```
GIT_LOG_COMMAND = [
    'git',
    'log',
    '--pretty=format:*****%n%H%n%P%n%aN%n%ae%n%aI%n',
    '--numstat',
    '--no-color',
    '--all']

GIT_COMMIT_SEPARATOR = '*****'


def run_git_log(repo_dir: Path) -> str:
    """
    Execute the git log command (defined by ``GIT_LOG_COMMAND``) inside the
    given repository.

    Returns the log in case of success or None otherwise.
    """
    p = subprocess.run(GIT_LOG_COMMAND, cwd=repo_dir,
                       capture_output=True, encoding='utf-8')
    if p.returncode == 0:
        return p.stdout
    else:
        return None


class BaseGitCommitParser:

    def parse_commit(self, commit: list) -> GitCommit:
        raise NotImplementedError('Subclasses must implement this method.')


class GitCommitParser(BaseGitCommitParser):

    # Pattern to parse diff
    STAT_ENTRY_RE = re.compile(r'(\d+)\t(\d+)\t(.+)')

    def _parse_diff(self, c):
        builder = GitDiffBuilder()
        for l in c:
            m = GitCommitParser.STAT_ENTRY_RE.match(l)
            if m:
                builder.add_entry(m[2], int(m[0]), int(m[1]))
            else:
                break
        return builder.build()

    def parse_commit(self, commit: list) -> GitCommit:
        c = iter(commit)
        id = next(c)
        parents = next(c).split(' ')
        author = next(c)
        author_email = next(c)
        author_date = parse_iso_date(next(c))
        author = next(c)
        next(c)
        return GitCommit(id, parents, author_date,
                         GitAuthor(author_email, author), self._parse_diff(c))


class GitLogParser:

    def __init__(self, commit_parser: BaseGitCommitParser) -> None:
        self._result = []
        self._commit_parser = commit_parser

    def _process_commit(self, commit: list) -> GitCommit:
        if commit is not None and commit:
            try:
                c = self._commit_parser.parse_commit(commit)
                self._result.append(c)
            except ValueError:
                LOGGER.warn(f'Invalid entry ${commit}.')

    def _split_commit(self, source: str) -> None:
        commit = list()
        for l in source.split('\n'):
            l = l.rstrip()
            if l == GIT_COMMIT_SEPARATOR:
                self._process_commit(commit)
                commit.clear()
            else:
                commit.append(l)
        if commit:
            self._process_commit(commit)

    def run(self, source: str) -> bool:
        self._result.clear()
        self._split_commit(source)
        return True

    def run_git(self, repo_dir: Path) -> bool:
        source = run_git_log(repo_dir)
        if source:
            return self.run(source)
        else:
            return False

    @ property
    def result(self) -> list:
        return self._result
