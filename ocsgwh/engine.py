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
from pathlib import Path
from .git import is_git_repo
from .git.model import GitLog
from .git.parser import GitLogParser, GitExecutionError, LOGGER

from logging import getLogger
LOGGER = getLogger(__name__)


class EngineError(Exception):

    def __init__(self, message: str, return_code: int = 1) -> None:
        super().__init__(message)
        self.return_code = return_code


class Options:
    def __init__(self, repo_dir: Path, output_dir: Path) -> None:
        self.repo_dir = repo_dir
        self.output_dir = output_dir

    def is_output_dir_valid(self, dir: Path):
        return not dir.exists() or dir.is_dir()

    def check_options(self):
        if not is_git_repo(self.repo_dir):
            raise EngineError(
                f'"{self.repo_dir}" does not point to a valid Git repository.')
        if not self.is_output_dir_valid(self.output_dir):
            raise EngineError(
                f'"{self.output_dir}" is not a valid output directory.')


class Engine:

    def __init__(self, options: Options) -> None:
        self.options = options

    def get_git_log(self) -> GitLog:
        parser = GitLogParser()
        try:
            if parser.run_git(self.options.repo_dir):
                return parser.build_git_log()
            else:
                raise EngineError(
                    f'Unable to parse the output of git log command.')
        except GitExecutionError as err:
            raise EngineError(
                str(err))

    def prepare_output_dir(self):
        dir = self.options.output_dir
        if not dir.is_dir():
            dir.mkdir(parents=True)

    def run(self) -> int:
        self.options.check_options()
        self.prepare_output_dir()
        log = self.get_git_log()

        print(log)
