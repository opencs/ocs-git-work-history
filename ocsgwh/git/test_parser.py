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
import unittest
import tempfile
from datetime import datetime, timedelta, timezone
from .parser import *
from ..test_utils import SAMPLE_DIR, ROOT_DIR


class TestParse(unittest.TestCase):

    def test_parse_iso_date(self):
        d1 = parse_iso_date('2021-01-21T14:24:07-03:00')
        d2 = datetime(year=2021, month=1, day=21,
                      hour=14, minute=24, second=7, tzinfo=timezone(timedelta(hours=-3)))
        self.assertEqual(d1, d2)

    def test_run_into_myself(self):
        s = run_git_log(ROOT_DIR)
        self.assertIsNotNone(s)

        s = run_git_log(tempfile.gettempdir())
        self.assertIsNone(s)


if __name__ == '__main__':
    unittest.main()
