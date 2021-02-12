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

    def test_same(self):
        d1 = GitDiffEntry('file', 1, 2)
        d2 = GitDiffEntry('file', 3, 4)
        d3 = GitDiffEntry('file1', 1, 2)

        self.assertTrue(d1.same(d1))
        self.assertTrue(d1.same(d2))
        self.assertTrue(d2.same(d1))
        self.assertFalse(d1.same(d3))
        self.assertFalse(d3.same(d1))

    def test_merge(self):
        d1 = GitDiffEntry('file', 1, 2)
        d2 = GitDiffEntry('file', 3, 4)
        d3 = d1.merge(d2)

        self.assertEqual(d3.file_name, d1.file_name)
        self.assertEqual(d3.added, d1.added + d2.added)
        self.assertEqual(d3.deleted, d1.deleted + d2.deleted)

        d4 = GitDiffEntry('file1', 3, 4)
        self.assertRaises(ValueError, d1.merge, d4)


class TestGitDiff(unittest.TestCase):

    def test_constructor(self):
        d = GitDiff()
        self.assertEqual(d.added, 0)
        self.assertEqual(d.deleted, 0)
        self.assertEqual(d.changed, 0)
        self.assertEqual(len(d), 0)
        self.assertFalse(d)

    def test_add(self):
        d = GitDiff()

        d.add(GitDiffEntry('file1', 1, 2))
        self.assertEqual(d.added, 1)
        self.assertEqual(d.deleted, 2)
        self.assertEqual(d.changed, d.added + d.deleted)
        self.assertEqual(len(d), 1)
        self.assertTrue(d)

        e = d['file1']
        self.assertEqual(e.file_name, 'file1')
        self.assertEqual(e.added, 1)
        self.assertEqual(e.deleted, 2)

        d.add(GitDiffEntry('file1', 3, 4))
        self.assertEqual(d.added, 1 + 3)
        self.assertEqual(d.deleted, 2 + 4)
        self.assertEqual(d.changed, d.added + d.deleted)
        self.assertEqual(len(d), 1)
        self.assertTrue(d)

        e = d['file1']
        self.assertEqual(e.file_name, 'file1')
        self.assertEqual(e.added, 1 + 3)
        self.assertEqual(e.deleted, 2 + 4)

        d.add(GitDiffEntry('file2', 5, 6))
        self.assertEqual(d.added, 1 + 3 + 5)
        self.assertEqual(d.deleted, 2 + 4 + 6)
        self.assertEqual(d.changed, d.added + d.deleted)
        self.assertEqual(len(d), 2)
        self.assertTrue(d)

        e = d['file1']
        self.assertEqual(e.file_name, 'file1')
        self.assertEqual(e.added, 1 + 3)
        self.assertEqual(e.deleted, 2 + 4)

        e = d['file2']
        self.assertEqual(e.file_name, 'file2')
        self.assertEqual(e.added, 5)
        self.assertEqual(e.deleted, 6)

    def test_iter(self):
        d = GitDiff()
        d.add(GitDiffEntry('file1', 1, 2))
        d.add(GitDiffEntry('file2', 3, 4))

        files = set()
        for e in d:
            self.assertFalse(e.file_name in files)
            files.add(e.file_name)
        self.assertEquals(len(files), 2)
        self.assertTrue('file1' in files)
        self.assertTrue('file2' in files)

    def test_merge(self):
        d1 = GitDiff()
        d1.add(GitDiffEntry('file1', 1, 2))
        d1.add(GitDiffEntry('file2', 3, 4))

        d2 = GitDiff()
        d2.add(GitDiffEntry('file1', 5, 6))
        d2.add(GitDiffEntry('file3', 7, 8))

        d3 = d1.merge(d2)
        self.assertEquals(len(d1), 2)
        e = d1['file1']
        self.assertEqual(e.added, 1)
        self.assertEqual(e.deleted, 2)
        e = d1['file2']
        self.assertEqual(e.added, 3)
        self.assertEqual(e.deleted, 4)

        self.assertEquals(len(d2), 2)
        e = d2['file1']
        self.assertEqual(e.added, 5)
        self.assertEqual(e.deleted, 6)
        e = d2['file3']
        self.assertEqual(e.added, 7)
        self.assertEqual(e.deleted, 8)

        self.assertEquals(len(d3), 3)
        e = d3['file1']
        self.assertEqual(e.added, 1 + 5)
        self.assertEqual(e.deleted, 2 + 6)
        e = d3['file2']
        self.assertEqual(e.added, 3)
        self.assertEqual(e.deleted, 4)
        e = d3['file3']
        self.assertEqual(e.added, 7)
        self.assertEqual(e.deleted, 8)


if __name__ == '__main__':
    unittest.main()
