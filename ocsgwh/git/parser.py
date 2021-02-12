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


def parse_iso_date(s):
    """
    Parses a strict ISO date (e.g.: '2021-01-21T14:24:07-03:00').
    """
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S%z')


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
