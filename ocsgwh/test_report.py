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
from .git.model import *
from .git.test_model import get_sample_git_log
from .report import *


class TestDiffSummary(unittest.TestCase):

    def test_contructor(self):
        r = DiffSummary()
        self.assertEqual(r.added, 0)
        self.assertEqual(r.deleted, 0)
        self.assertEqual(r.changed, r.added + r.deleted)

        r = DiffSummary(1, 2)
        self.assertEqual(r.added, 1)
        self.assertEqual(r.deleted, 2)
        self.assertEqual(r.changed, r.added + r.deleted)

    def test_update_with_entry(self):
        r = DiffSummary()
        d = GitDiffEntry('file', 1, 2)

        r.update_with_entry(d)
        self.assertEqual(r.added, 1)
        self.assertEqual(r.deleted, 2)
        self.assertEqual(r.changed, r.added + r.deleted)

        r.update_with_entry(d)
        self.assertEqual(r.added, 2)
        self.assertEqual(r.deleted, 4)
        self.assertEqual(r.changed, r.added + r.deleted)

    def test_update_with_diff(self):
        r = DiffSummary()
        db = GitDiffBuilder()
        db.add_entry('file', 1, 2)
        db.add_entry('file2', 3, 4)

        r.update_with_diff(db.build())
        self.assertEqual(r.added, 4)
        self.assertEqual(r.deleted, 6)
        self.assertEqual(r.changed, r.added + r.deleted)
