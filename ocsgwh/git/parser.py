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
import datetime
import subprocess
from pathlib import Path
from .model import *

AUTHOR_VALUE_PATTERN = re.compile(r'^([^<]+) <([^>]+)>$')


def parse_iso_date(s):
    """
    Parses a Git date when the parameter '--date=iso' is used.
    """
    # Example of date with --date=iso: '2020-12-17 19:19:19 -0300'
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S %z')


def parse_commit(s):
    # commit 5a4b7b3713154a0b89d0214556eee78aa451e28d
    # commit 5a4b7b3713154a0b89d0214556eee78aa451e28d (bitbucket/swagger, swagger)
    pass


GIT_LOG_COMMAND = [
    'git',
    'log',
    '--pretty=format:*****%n%H%n%P%n%aN%n%ae%n%aI%n',
    '--numstat',
    '--no-color',
    '--all']

# git log --pretty=format:*****%H%n%P%n%aN%n%ae%n%aI%n --numstat --no-color --all
# *****
# Commit id
# Parent ids
# Author Name
# Author email
# Author Date: ISO
#
# add   sub     file


def run_git_log(repo_dir: Path) -> str:
    """
    Execute the git log command inside the given repository.

    Returns the log in case of success or None otherwise.
    """
    p = subprocess.run(GIT_LOG_COMMAND, cwd=repo_dir,
                       capture_output=True, encoding='utf-8')
    if p.returncode == 0:
        return p.stdout
    else:
        return None
