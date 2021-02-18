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
import argparse
from ocsgwh.versioninfo import VERSION
import sys
from pathlib import Path
from ocsgwh import Engine, Options, EngineError
PROGRAM_DESC = \
    '%(prog)s - A Git work history report generator\n' + \
    f'Version: {VERSION}\n' \
    'Copyright (C) 2021 Open Communications Security'
LICENSE_DESC = """
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under the terms of GNU GENERAL PUBLIC LICENSE, Version 3.
See <https://www.gnu.org/licenses/> for further detais.
"""

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=PROGRAM_DESC,
    epilog=LICENSE_DESC)
parser.add_argument('git_repo', metavar='<repository dir>', type=Path,
                    help='Git repository directory.')
parser.add_argument('output_dir', metavar='<output directory>', type=Path,
                    help='Output directory.')
parser.add_argument('-t', metavar='<report title>', type=str,
                    dest='title', default=None,
                    help='Output directory.')

if __name__ == '__main__':
    args = parser.parse_args()
    options = Options(args.git_repo, args.output_dir, args.title)
    engine = Engine(options)
    try:
        engine.run()
    except EngineError as err:
        sys.stderr.write(f'{err}\n')
        sys.exit(err.return_code)
