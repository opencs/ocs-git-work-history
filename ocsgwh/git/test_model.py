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
from .test_parser import get_sample_log


class TestGitAuthor(unittest.TestCase):

    def test_constructor(self):
        a = GitAuthor('email', 'name')
        self.assertEqual(a.email, 'email')
        self.assertEqual(a.name, 'name')

    def test_equal(self):
        a1 = GitAuthor('email1', 'name1')
        a2 = GitAuthor('email1', 'name1')
        a3 = GitAuthor('email3', 'name2')

        self.assertEqual(a1, a1)
        self.assertEqual(a1, a2)
        self.assertEqual(a2, a1)
        self.assertNotEqual(a1, a3)

    def test_hash(self):
        a1 = GitAuthor('email1', 'name1')
        a2 = GitAuthor('email1', 'name1')

        self.assertEqual(hash(a1), hash(a2))


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


class TestGitCommit(unittest.TestCase):

    def test_contructor(self):
        b = GitDiffBuilder()
        id = 'id'
        parents = ['parent1', 'parent2']
        author = GitAuthor('email', 'author')
        timestamp = datetime.now()
        diff = b.build()
        c = GitCommit(id, parents, timestamp, author, diff)
        self.assertEqual(c.id, id)
        self.assertEqual(c.parents, parents)
        self.assertEqual(c.timestamp, timestamp)
        self.assertEqual(c.author.email, author.email)
        self.assertEqual(c.author.name, author.name)
        self.assertEqual(len(c.diff), len(diff))

        b.add_entry('file', 1, 2)
        diff = b.build()
        c = GitCommit(id, parents, timestamp, author, diff)
        self.assertEqual(c.id, id)
        self.assertEqual(c.parents, parents)
        self.assertEqual(c.timestamp, timestamp)
        self.assertEqual(c.author.email, author.email)
        self.assertEqual(c.author.name, author.name)
        self.assertEqual(len(c.diff), len(diff))
        self.assertEqual(c.diff[0].file_name, diff[0].file_name)

    def test_commit_type(self):
        b = GitDiffBuilder()
        id = 'id'
        author = GitAuthor('email', 'author')
        timestamp = datetime.now()
        diff = b.build()

        c = GitCommit(id, [], timestamp, author, diff)
        self.assertEqual(c.commit_type, GitCommitType.ROOT)

        c = GitCommit(id, ['1234'], timestamp, author, diff)
        self.assertEqual(c.commit_type, GitCommitType.NORMAL)

        c = GitCommit(id, ['1234', '5678'], timestamp, author, diff)
        self.assertEqual(c.commit_type, GitCommitType.MERGE)

        c = GitCommit(id, ['1234', '5678', '9012'], timestamp, author, diff)
        self.assertEqual(c.commit_type, GitCommitType.MERGE)


class TestGitLog(unittest.TestCase):

    def test_constructor(self):
        l = GitLog([])
        self.assertFalse(l)
        self.assertFalse(l.authors)

        l = GitLog(get_sample_log())
        self.assertTrue(l)
        self.assertEqual(len(l), 67)
        self.assertTrue(l.authors)
        self.assertEqual(len(l.authors), 4)

        self.assertEqual(l[0].timestamp, l.min_date)
        self.assertEqual(l[-1].timestamp, l.max_date)
        # Ensure it is sorted by date.
        last_date = l[0].timestamp
        for c in l:
            t = c.timestamp
            self.assertGreaterEqual(t, last_date)
            last_date = t

        print(l.authors)

    def test_by_type(self):
        src = GitLog(get_sample_log())

        for t in list(GitCommitType):
            l = src.by_type(t)
            for c in l:
                self.assertEqual(c.commit_type, t)

    def test_by_author(self):
        src = GitLog(get_sample_log())

        for an in src.authors:
            for a in an.authors:
                l = src.by_author(a)
                #self.assertEqual(l.authors, [a])
                for c in l:
                    self.assertEqual(c.author, a)

    def test_by_date(self):
        src = GitLog(get_sample_log())

        start_date = src[10].timestamp.date()
        end_date = src[20].timestamp.date()

        l = src.by_date(start_date, end_date)
        for c in l:
            self.assertGreaterEqual(c.timestamp.date(), start_date)
            self.assertLess(c.timestamp.date(), end_date)


if __name__ == '__main__':
    unittest.main()
