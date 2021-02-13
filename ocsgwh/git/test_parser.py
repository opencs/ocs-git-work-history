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


class TestFunctions(unittest.TestCase):

    def test_parse_iso_date(self):
        d1 = parse_iso_date('2021-01-21T14:24:07-03:00')
        d2 = datetime(year=2021, month=1, day=21,
                      hour=14, minute=24, second=7, tzinfo=timezone(timedelta(hours=-3)))
        self.assertEqual(d1, d2)

        self.assertRaises(ValueError, parse_iso_date,
                          '2021-01-21 14:24:07-03:00')

    def test_run_into_myself(self):
        s = run_git_log(ROOT_DIR)
        self.assertIsNotNone(s)

        s = run_git_log(tempfile.gettempdir())
        self.assertIsNone(s)


class TestGitCommitParser(unittest.TestCase):

    def test__parse_diff_empty(self):
        p = GitCommitParser()

        d = p._parse_diff(iter([]))
        self.assertFalse(d)

        d = p._parse_diff(iter(['']))
        self.assertFalse(d)

        d = p._parse_diff(iter(['invalid']))
        self.assertFalse(d)

    def test__parse_diff(self):
        p = GitCommitParser()

        d = p._parse_diff(iter([
            '1\t2\tfile1',
            '3\t4\tfile1',
            '5\t6\tfile0',
        ]))
        self.assertEqual(len(d), 2)
        self.assertEqual(d[0].file_name, 'file0')
        self.assertEqual(d[0].added, 5)
        self.assertEqual(d[0].deleted, 6)
        self.assertEqual(d[1].file_name, 'file1')
        self.assertEqual(d[1].added, 4)
        self.assertEqual(d[1].deleted, 6)

        d = p._parse_diff(iter([
            '1\t2\tfile1',
            '3\t4\tfile1',
            '5\t6\tfile0',
            ''
        ]))
        self.assertEqual(len(d), 2)
        self.assertEqual(d[0].file_name, 'file0')
        self.assertEqual(d[0].added, 5)
        self.assertEqual(d[0].deleted, 6)
        self.assertEqual(d[1].file_name, 'file1')
        self.assertEqual(d[1].added, 4)
        self.assertEqual(d[1].deleted, 6)

        d = p._parse_diff(iter([
            '1\t2\tfile1',
            '3\t4\tfile1',
            '5\t6\tfile0',
            'invalid',
            '1\t2\tfile1',
            '3\t4\tfile1',
            '5\t6\tfile0',
        ]))
        self.assertEqual(len(d), 2)
        self.assertEqual(d[0].file_name, 'file0')
        self.assertEqual(d[0].added, 5)
        self.assertEqual(d[0].deleted, 6)
        self.assertEqual(d[1].file_name, 'file1')
        self.assertEqual(d[1].added, 4)
        self.assertEqual(d[1].deleted, 6)

    def test_parse_id(self):
        p = GitCommitParser()

        s = 'cee812a745058215d6c62adab103cccf23e9db02'
        self.assertEqual(p._parse_id(s), s)
        self.assertRaises(ValueError, p._parse_id,
                          'cee812a745058215d6c62adab103cccf23e9db0')
        self.assertRaises(ValueError, p._parse_id,
                          'cee812a745058215d6c62adab103cccf 23e9db0')

    def test_parse_parent(self):
        p = GitCommitParser()

        self.assertEqual(p._parse_parent(
            'ff53cd91a8906faa04e63331feb25216cb384150 e08b051a6305e132d6a5d0002c5f62f701b5cb43'),
            ['ff53cd91a8906faa04e63331feb25216cb384150', 'e08b051a6305e132d6a5d0002c5f62f701b5cb43'])
        self.assertRaises(ValueError, p._parse_parent,
                          '')
        self.assertRaises(ValueError, p._parse_parent,
                          'ff53cd91a8906faa04e63331feb25216cb384150  e08b051a6305e132d6a5d0002c5f62f701b5cb43')
        self.assertRaises(ValueError, p._parse_parent,
                          'ff53cd91a8906faa04e63331feb25216cb38415 e08b051a6305e132d6a5d0002c5f62f701b5cb43')
        self.assertRaises(ValueError, p._parse_parent,
                          'ff53cd91a8906faa04e63331feb25216cb384150  e08b051a6305e132d6a5d0002c5f62f701b5cb4')
        self.assertRaises(ValueError, p._parse_parent,
                          'ff53cd91a8906faa 4e63331feb25216cb384150  e08b051a6305e132d6a5d0002c5f62f701b5cb43')
        self.assertRaises(ValueError, p._parse_parent,
                          'ff53cd91a8906faa04e63331feb25216cb384150  e08b051a6305e132d6a5d0002c5f62 701b5cb43')

    def test_parse_name(self):
        p = GitCommitParser()

        s = 'a'
        self.assertEqual(p._parse_name(s), s)
        self.assertEqual(p._parse_name(' a '), 'a')
        self.assertRaises(ValueError, p._parse_name,
                          '')
        self.assertRaises(ValueError, p._parse_name,
                          '    ')
        self.assertRaises(ValueError, p._parse_name,
                          '    ')

    def test_parse(self):
        p = GitCommitParser()

        d = p.parse([
            'cee812a745058215d6c62adab103cccf23e9db02',
            'ff53cd91a8906faa04e63331feb25216cb384150 e08b051a6305e132d6a5d0002c5f62f701b5cb43',
            'Ruy Barbosa de Oliveira',
            'ruy.barbosa@email.com',
            '2021-01-22T00:56:54+00:00',
            '',
        ])
        self.assertEqual(d.id, 'cee812a745058215d6c62adab103cccf23e9db02')
        self.assertEqual(d.parents, [
                         'ff53cd91a8906faa04e63331feb25216cb384150', 'e08b051a6305e132d6a5d0002c5f62f701b5cb43'])
        self.assertEqual(d.author.name, 'Ruy Barbosa de Oliveira')
        self.assertEqual(d.author.email, 'ruy.barbosa@email.com')
        self.assertEqual(d.timestamp, parse_iso_date(
            '2021-01-22T00:56:54+00:00'))
        self.assertFalse(d.diff)

        d = p.parse([
            'cee812a745058215d6c62adab103cccf23e9db02',
            'ff53cd91a8906faa04e63331feb25216cb384150',
            'Ruy Barbosa de Oliveira',
            'ruy.barbosa@email.com',
            '2021-01-22T00:56:54+00:00',
            '',
            '1\t2\tfile1',
            '3\t4\tfile1',
            '5\t6\tfile0',
            ''
        ])
        self.assertEqual(d.id, 'cee812a745058215d6c62adab103cccf23e9db02')
        self.assertEqual(d.parents, [
                         'ff53cd91a8906faa04e63331feb25216cb384150'])
        self.assertEqual(d.author.name, 'Ruy Barbosa de Oliveira')
        self.assertEqual(d.author.email, 'ruy.barbosa@email.com')
        self.assertEqual(d.timestamp, parse_iso_date(
            '2021-01-22T00:56:54+00:00'))
        self.assertEqual(len(d.diff), 2)
        self.assertEqual(d.diff[0].file_name, 'file0')
        self.assertEqual(d.diff[0].added, 5)
        self.assertEqual(d.diff[0].deleted, 6)
        self.assertEqual(d.diff[1].file_name, 'file1')
        self.assertEqual(d.diff[1].added, 4)
        self.assertEqual(d.diff[1].deleted, 6)

    def test_parse_failures(self):
        p = GitCommitParser()

        self.assertRaises(
            ValueError, p.parse,
            [
                'cee812a745058215d6c62adab103cccf23e9db02',
                'ff53cd91a8906faa04e63331feb25216cb384150 e08b051a6305e132d6a5d0002c5f62f701b5cb43',
                'Ruy Barbosa de Oliveira',
                'ruy.barbosa@email.com',
                '2021-01-22T00:56:54+00:00',
            ]
        )

        self.assertRaises(
            ValueError, p.parse,
            [
                'cee812a74505821 d6c62adab103cccf23e9db02',
                'ff53cd91a8906faa04e63331feb25216cb384150 e08b051a6305e132d6a5d0002c5f62f701b5cb43',
                'Ruy Barbosa de Oliveira',
                'ruy.barbosa@email.com',
                '2021-01-22T00:56:54+00:00',
                ''
            ]
        )

        self.assertRaises(
            ValueError, p.parse,
            [
                'cee812a745058215d6c62adab103cccf23e9db02',
                'ff53cd91a8906faa04 63331feb25216cb384150 e08b051a6305e132d6a5d0002c5f62f701b5cb43',
                'Ruy Barbosa de Oliveira',
                'ruy.barbosa@email.com',
                '2021-01-22T00:56:54+00:00',
                ''
            ]
        )

        self.assertRaises(
            ValueError, p.parse,
            [
                'cee812a745058215d6c62adab103cccf23e9db02',
                'ff53cd91a8906faa04e63331feb25216cb384150 e08b051a6305e132d6a5d0002c5f62f701b5cb43',
                '',
                'ruy.barbosa@email.com',
                '2021-01-22T00:56:54+00:00',
                ''
            ]
        )

        self.assertRaises(
            ValueError, p.parse,
            [
                'cee812a745058215d6c62adab103cccf23e9db02',
                'ff53cd91a8906faa04e63331feb25216cb384150 e08b051a6305e132d6a5d0002c5f62f701b5cb43',
                'Ruy Barbosa de Oliveira',
                '',
                '2021-01-22T00:56:54+00:00',
                ''
            ]
        )

        self.assertRaises(
            ValueError, p.parse,
            [
                'cee812a745058215d6c62adab103cccf23e9db02',
                'ff53cd91a8906faa04e63331feb25216cb384150 e08b051a6305e132d6a5d0002c5f62f701b5cb43',
                'Ruy Barbosa de Oliveira',
                'ruy.barbosa@email.com',
                '2 21-01-22T00:56:54+00:00',
                ''
            ]
        )


if __name__ == '__main__':
    unittest.main()
