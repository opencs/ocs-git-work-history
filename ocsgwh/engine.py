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
from logging import getLogger
from shutil import copyfile
from .git.parser import GitLogParser, GitExecutionError, LOGGER
from .git.model import GitLog
from .git import is_git_repo
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Template

from logging import getLogger
LOGGER = getLogger(__name__)
TEMPLATE_DIR = Path(__file__).parent / 'templates'


class EngineError(Exception):

    def __init__(self, message: str, return_code: int = 1) -> None:
        super().__init__(message)
        self.return_code = return_code


class Options:
    def __init__(self, repo_dir: Path, output_dir: Path) -> None:
        self.repo_dir = repo_dir
        self.output_dir = output_dir
        self.template_dir = TEMPLATE_DIR

    def is_output_dir_valid(self, dir: Path):
        return not dir.exists() or dir.is_dir()

    def check_options(self):
        if not is_git_repo(self.repo_dir):
            raise EngineError(
                f'"{self.repo_dir}" does not point to a valid Git repository.')
        if not self.is_output_dir_valid(self.output_dir):
            raise EngineError(
                f'"{self.output_dir}" is not a valid output directory.')


STATIC_EXTENSIONS = ['.css', '.png', '.svg', '.jpg']


class Engine:

    def __init__(self, options: Options) -> None:
        self.options = options
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.options.template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

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

    def get_template(self, template_name: str) -> Template:
        return self.jinja_env.get_template(template_name)

    def run(self) -> int:
        self.options.check_options()
        self.prepare_output_dir()
        log = self.get_git_log()
        self.basic_template_vars = {'repository_dir': str(
            self.options.repo_dir.absolute()), 'report_date': datetime.now()}

        self.deploy_static_files(self.options.output_dir)
        self.render_template('index.html', 'index.html', {})

    def render_template(self, template_name, file_name: str, vars: dict):
        template = self.get_template(template_name)
        template_vars = {**self.basic_template_vars, **vars}
        out_file = self.options.output_dir / file_name
        with open(out_file, 'w', encoding='utf-8') as outp:
            outp.write(template.render(**template_vars))

    def deploy_static_files(self, target_dir: Path):
        files = [f for f in TEMPLATE_DIR.iterdir() if f.is_file()]
        static_files = [f for f in files if f.suffix in STATIC_EXTENSIONS]
        for f in static_files:
            copyfile(f, target_dir / f.name)
