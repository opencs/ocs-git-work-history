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
from .model import *


class TestGitAuthor(unittest.TestCase):

    def test_constructor(self):
        a = GitAuthor('email', 'name')
        self.assertEqual(a.email, 'email')
        self.assertEqual(a.name, 'name')

    def test_same(self):
        a1 = GitAuthor('email1', 'name1')
        a2 = GitAuthor('email1', 'name2')
        a3 = GitAuthor('email2', 'name1')

        self.assertTrue(a1.same(a1))
        self.assertTrue(a1.same(a2))
        self.assertTrue(a2.same(a1))
        self.assertFalse(a1.same(a3))
        self.assertFalse(a3.same(a1))


class TestGitDiffEntry(unittest.TestCase):

    def test_constructor(self):
        d = GitDiffEntry('file', 1, 2)
        self.assertEqual(d.file_name, 'file')
        self.assertEqual(d.added, 1)
        self.assertEqual(d.deleted, 2)
        self.assertEqual(d.changed, 3)

    def test_eq(self):
        d1 = GitDiffEntry('file1', 1, 2)
        d2 = GitDiffEntry('file1', 1, 2)
        d3 = GitDiffEntry('file2', 1, 2)
        d4 = GitDiffEntry('file1', 2, 2)
        d5 = GitDiffEntry('file1', 1, 3)

        self.assertEqual(d1, d1)
        self.assertEqual(d1, d2)
        self.assertEqual(d2, d1)
        self.assertNotEqual(d1, d3)
        self.assertNotEqual(d1, d4)
        self.assertNotEqual(d1, d5)


class TestGitDiff(unittest.TestCase):

    def create_sample_entries(n: int):
        l = []
        for i in range(n):
            l.append(GitDiffEntry('file' + str(i), i + 10, i))
        return l

    def test_constructor(self):
        d = GitDiff([])
        self.assertEqual(d.added, 0)
        self.assertEqual(d.deleted, 0)
        self.assertEqual(d.changed, d.added + d.deleted)
        self.assertEqual(len(d), 0)
        self.assertFalse(d)

        d = GitDiff(TestGitDiff.create_sample_entries(5))
        self.assertEqual(d.added, 10 + 50)
        self.assertEqual(d.deleted, 10)
        self.assertEqual(d.changed, d.added + d.deleted)
        self.assertEqual(len(d), 5)
        self.assertTrue(d)

    def test_access(self):
        l = TestGitDiff.create_sample_entries(5)
        d = GitDiff(l)

        for i in range(len(d)):
            self.assertEqual(d[i], l[i])

        li = iter(l)
        for i in d:
            self.assertEqual(i, next(li))


class TestGitDiffBuilder(unittest.TestCase):

    def test_empty(self):
        b = GitDiffBuilder()
        d = b.build()
        self.assertFalse(d)

    def test_add_entry(self):
        b = GitDiffBuilder()

        b.add_entry('file1', 1, 2)
        d = b.build()
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0].file_name, 'file1')
        self.assertEqual(d[0].added, 1)
        self.assertEqual(d[0].deleted, 2)

        b.add_entry('file1', 1, 2)
        d = b.build()
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0].file_name, 'file1')
        self.assertEqual(d[0].added, 2)
        self.assertEqual(d[0].deleted, 4)

        b.add_entry('file0', 3, 5)
        d = b.build()
        self.assertEqual(len(d), 2)
        self.assertEqual(d[0].file_name, 'file0')
        self.assertEqual(d[0].added, 3)
        self.assertEqual(d[0].deleted, 5)
        self.assertEqual(d[1].file_name, 'file1')
        self.assertEqual(d[1].added, 2)
        self.assertEqual(d[1].deleted, 4)

    def test_add_diff_entry(self):
        b = GitDiffBuilder()
        d1 = GitDiffEntry('file1', 1, 2)
        d2 = GitDiffEntry('file0', 3, 5)

        b.add_diff_entry(d1)
        d = b.build()
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0].file_name, 'file1')
        self.assertEqual(d[0].added, 1)
        self.assertEqual(d[0].deleted, 2)

        b.add_diff_entry(d1)
        d = b.build()
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0].file_name, 'file1')
        self.assertEqual(d[0].added, 2)
        self.assertEqual(d[0].deleted, 4)

        b.add_diff_entry(d2)
        d = b.build()
        self.assertEqual(len(d), 2)
        self.assertEqual(d[0].file_name, 'file0')
        self.assertEqual(d[0].added, 3)
        self.assertEqual(d[0].deleted, 5)
        self.assertEqual(d[1].file_name, 'file1')
        self.assertEqual(d[1].added, 2)
        self.assertEqual(d[1].deleted, 4)

    def test_add_diff(self):
        b = GitDiffBuilder()

        b.add_entry('file0', 1, 2).add_entry('file1', 3, 4)
        d1 = b.build()
        b.add_diff(d1)
        d2 = b.build()

        self.assertEqual(len(d2), 2)
        self.assertEqual(d2[0].file_name, 'file0')
        self.assertEqual(d2[0].added, 2)
        self.assertEqual(d2[0].deleted, 4)
        self.assertEqual(d2[1].file_name, 'file1')
        self.assertEqual(d2[1].added, 6)
        self.assertEqual(d2[1].deleted, 8)


if __name__ == '__main__':
    unittest.main()
