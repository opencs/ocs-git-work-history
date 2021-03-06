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


class TestGitAuthorName(unittest.TestCase):

    def test_constructor(self):
        authors = [GitAuthor('email', 'alan MathisOn  Turing'),
                   GitAuthor('email1', 'alan MathisOn  Turing')]
        an = GitAuthorName('Alan Mathison Turing',
                           authors)

        self.assertEqual(an.name, 'Alan Mathison Turing')
        self.assertEqual(an.authors, authors)
        self.assertEqual(len(an._author_set), len(authors))

    def test_contains(self):
        authors = [GitAuthor('email', 'alan MathisOn  Turing'),
                   GitAuthor('email1', 'alan MathisOn  Turing')]
        an = GitAuthorName('Alan Mathison Turing',
                           authors)
        out = GitAuthor('email3', 'alan MathisOn  Turing')

        for a in authors:
            self.assertTrue(a in an)
        self.assertFalse(out in an)

    def test_hashable_order(self):
        a1 = GitAuthorName('Alan Mathison  Turing', [
                           GitAuthor('email1', 'alan MathisOn  Turing')])
        a2 = GitAuthorName('Alan Mathison  Turing', [
                           GitAuthor('email1', 'alan MathisOn Turing')])
        a3 = GitAuthorName('Blan Mathison Turing', [
                           GitAuthor('email1', 'blan MathisOn Turing')])

        self.assertEqual(a1, a1)
        self.assertEqual(a2, a1)
        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, a3)
        self.assertNotEqual(a2, a3)
        self.assertEqual(hash(a1), hash(a2))
        self.assertLess(a1, a3)


class TestComparableGitAuthor(unittest.TestCase):
    def test_normalize_name(self):
        self.assertEqual(ComparableGitAuthor.normalize_name(
            'alan MathisOn  Turing'), 'Alan Mathison Turing')

    def test_constructor(self):
        author = GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing')
        a = ComparableGitAuthor(author)

        self.assertEqual(a.author, author)
        self.assertEqual(a.name, 'Alan Mathison Turing')
        self.assertEqual(a.parts, ['Alan', 'Mathison', 'Turing'])

    def test_same_name(self):
        a1 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing'))
        a2 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan MathisOn Turing'))
        a3 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan Turing'))

        self.assertTrue(a1.same_name(a1))
        self.assertTrue(a1.same_name(a2))
        self.assertFalse(a1.same_name(a3))

    def test_same_email(self):
        a1 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing'))
        a2 = ComparableGitAuthor(
            GitAuthor('aturing@opencs.com.br ', 'alan MathisOn Turing'))
        a3 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan Turing'))

        self.assertTrue(a1.same_email(a1))
        self.assertTrue(a1.same_email(a2))
        self.assertFalse(a1.same_email(a3))

    def test_same_first_last(self):
        a1 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing'))
        a2 = ComparableGitAuthor(
            GitAuthor('aturing@opencs.com.br ', 'alan Turing'))
        a3 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan MathisOn  Turning'))
        a4 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alain MathisOn   Turing'))

        self.assertTrue(a1.same_first_last(a1))
        self.assertTrue(a1.same_first_last(a2))
        self.assertFalse(a1.same_first_last(a3))

    def test_match(self):
        a1 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing'))
        a2 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'A. Turing'))
        a3 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan MathisOn  Turing'))
        a4 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan Turing'))
        a5 = ComparableGitAuthor(
            GitAuthor('babagge@opencs.com.br', 'Charles Babbage'))

        self.assertEqual(a1.match(a1), 5)
        self.assertEqual(a1.match(a2), 4)
        self.assertEqual(a1.match(a3), 3)
        self.assertEqual(a1.match(a4), 2)
        self.assertEqual(a1.match(a5), 0)

    def test_match(self):
        a1 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing'))
        a2 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing'))
        a3 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan MathisOn  Turing'))
        a4 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn   Turing'))

        self.assertEqual(a1, a2)
        self.assertEqual(hash(a1), hash(a2))
        self.assertNotEqual(a1, a3)
        self.assertNotEqual(a1, a4)


class TestGitAuthorNameBuilder(unittest.TestCase):

    def test_constructor(self):
        b = GitAuthorNameBuilder()
        self.assertFalse(bool(b._authors))

    def test_try_add(self):
        b = GitAuthorNameBuilder()
        a1 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing'))
        a2 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'A. Turing'))
        a3 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan MathisOn  Turing'))
        a4 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan Turing'))
        a5 = ComparableGitAuthor(
            GitAuthor('babagge@opencs.com.br', 'Charles Babbage'))

        self.assertTrue(b.try_add(a1))
        self.assertTrue(a1 in b._authors)
        self.assertTrue(b.try_add(a1))
        self.assertTrue(a1 in b._authors)
        self.assertTrue(b.try_add(a2))
        self.assertTrue(a2 in b._authors)
        self.assertTrue(b.try_add(a3))
        self.assertTrue(a3 in b._authors)
        self.assertTrue(b.try_add(a4))
        self.assertTrue(a4 in b._authors)
        self.assertFalse(b.try_add(a5))
        self.assertTrue(a5 not in b._authors)

    def test_find_best_name(self):
        b = GitAuthorNameBuilder()
        a1 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing'))
        a2 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'A. Turing'))
        a3 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan MathisOn  Turing'))
        a4 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan Turing'))

        self.assertTrue(b.try_add(a1))
        self.assertTrue(b.try_add(a2))
        self.assertTrue(b.try_add(a3))
        self.assertTrue(b.try_add(a4))
        self.assertEqual(b.find_best_name(), 'Alan Mathison Turing')

    def test_get_author_list(self):
        b = GitAuthorNameBuilder()
        a1 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'alan MathisOn  Turing'))
        a2 = ComparableGitAuthor(
            GitAuthor('Aturing@opencs.com.br', 'A. Turing'))
        a3 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan MathisOn  Turing'))
        a4 = ComparableGitAuthor(
            GitAuthor('Aturing2@opencs.com.br', 'alan Turing'))

        self.assertTrue(b.try_add(a1))
        self.assertTrue(b.try_add(a2))
        self.assertTrue(b.try_add(a3))
        self.assertTrue(b.try_add(a4))
        l = b.get_author_list()
        self.assertEqual(l, [a2.author, a3.author, a1.author, a4.author])


class TestGitLog(unittest.TestCase):

    def test_constructor(self):
        l = GitLog([])
        self.assertFalse(l)
        self.assertFalse(l.authors)

        l = GitLog(get_sample_log())
        self.assertTrue(l)
        self.assertEqual(len(l), 67)

        # Test the authors list
        self.assertTrue(l.authors)
        self.assertEqual(len(l.authors), 4)
        for i in range(1, len(l.authors)):
            self.assertLess(l.authors[i - 1], l.authors[i])

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

    def test_by_authors(self):
        src = GitLog(get_sample_log())

        for an in src.authors:
            l = src.by_authors(an.authors)
            for c in l:
                self.assertTrue(c.author in an.authors)

    def test_by_author_name(self):
        src = GitLog(get_sample_log())

        for an in src.authors:
            l = src.by_author_name(an.authors)
            for c in l:
                self.assertTrue(c.author in an.authors)

    def test_by_date(self):
        src = GitLog(get_sample_log())

        start_date = src[10].timestamp.date()
        end_date = src[20].timestamp.date()

        l = src.by_date(start_date, end_date)
        for c in l:
            self.assertGreaterEqual(c.timestamp.date(), start_date)
            self.assertLess(c.timestamp.date(), end_date)


def get_sample_git_log():
    """
    Retuns the a GitLog instance based on the sample file.
    """
    return GitLog(get_sample_log())


if __name__ == '__main__':
    unittest.main()
