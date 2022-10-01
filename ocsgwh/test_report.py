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


class TestDiffSummaryValue(unittest.TestCase):

    def test_contructor(self):
        v = DiffSummaryValue()
        self.assertEqual(v.added, 0)
        self.assertEqual(v.deleted, 0)
        self.assertEqual(v.update_count, 0)
        self.assertEqual(v.changed, 0)

        v = DiffSummaryValue(1, 2)
        self.assertEqual(v.added, 1)
        self.assertEqual(v.deleted, 2)
        self.assertEqual(v.update_count, 0)
        self.assertEqual(v.changed, 3)

    def test_new(self):
        v = DiffSummaryValue.new()
        self.assertEqual(v.added, 0)
        self.assertEqual(v.deleted, 0)
        self.assertEqual(v.update_count, 0)
        self.assertEqual(v.changed, 0)

    def test_update(self):
        v = DiffSummaryValue.new()

        self.assertEqual(v.added, 0)
        self.assertEqual(v.deleted, 0)
        self.assertEqual(v.update_count, 0)
        self.assertEqual(v.changed, 0)

        uv = v
        v += DiffSummaryValue(1, 2)
        self.assertEqual(v.added, 1)
        self.assertEqual(v.deleted, 2)
        self.assertEqual(v.update_count, 1)
        self.assertEqual(v.changed, 3)
        self.assertEqual(id(v), id(uv))

        uv = v
        v += GitDiffEntry('file', 1, 2)
        self.assertEqual(v.added, 2)
        self.assertEqual(v.deleted, 4)
        self.assertEqual(v.update_count, 2)
        self.assertEqual(v.changed, 6)
        self.assertEqual(id(v), id(uv))

        uv = v
        v += GitDiff([GitDiffEntry('file', 1, 2), GitDiffEntry('file2', 1, 2)])
        self.assertEqual(v.added, 4)
        self.assertEqual(v.deleted, 8)
        self.assertEqual(v.update_count, 3)
        self.assertEqual(v.changed, 12)
        self.assertEqual(id(v), id(uv))
