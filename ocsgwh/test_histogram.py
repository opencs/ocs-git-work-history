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
from unittest.mock import MagicMock, call
from .historgram import *


class DateSequenceIteratorTest(unittest.TestCase):

    def test_basic(self):
        start = date(1994, 1, 26)
        end = date(1994, 2, 25)

        i = DateSequenceIterator(start, end)
        exp = start
        last = None

        try:
            while True:
                d = next(i)
                self.assertGreaterEqual(d, start)
                self.assertLessEqual(d, end)
                self.assertEqual(d, exp)
                exp = exp + ONE_DAY_DELTA
                last = d
        except StopIteration:
            self.assertEqual(last, end)

    def test_not_divisible(self):
        start = date(1994, 1, 26)
        end = date(1994, 2, 25)

        delta = timedelta(days=11)
        i = DateSequenceIterator(start, end, delta)
        exp = start
        last = None

        try:
            while True:
                d = next(i)
                self.assertGreaterEqual(d, start)
                self.assertLessEqual(d, end)
                self.assertEqual(d, exp)
                exp = exp + delta
                last = d
        except StopIteration:
            self.assertLess(last, end)
            self.assertGreater(last + delta, end)

    def test_for(self):
        start = date(1994, 1, 26)
        end = date(1994, 2, 25)

        i = DateSequenceIterator(start, end)
        exp = start
        last = None
        for d in i:
            self.assertGreaterEqual(d, start)
            self.assertLessEqual(d, end)
            self.assertEqual(d, exp)
            exp = exp + ONE_DAY_DELTA
            last = d
        self.assertEqual(last, end)


class TestHistogram(unittest.TestCase):

    def test_constructor(self):
        h = Histogram()
        self.assertFalse(h._entries)
        self.assertEqual(h._create_value_func(), 0)
        self.assertEqual(h._update_value_func(1, 2), 3)

        h = Histogram(lambda: 1234, lambda x, y, z: x + y + z)
        self.assertFalse(h._entries)
        self.assertEqual(h._create_value_func(), 1234)
        self.assertEqual(h._update_value_func(1, 2, 3), 6)

    def test_access_op(self):
        h = Histogram()

        h.group_key = MagicMock(wraps=h.group_key)
        h.on_new_key = MagicMock(wraps=h.on_new_key)
        for i in range(10):
            self.assertEqual(h[i], 0)
            self.assertEquals(h.group_key.call_args, call(i))
        self.assertFalse(h.on_new_key.called)

        h.group_key.reset_mock()
        h.on_new_key.reset_mock()
        for i in range(10):
            if i % 2 == 0:
                h[i] = 0
                self.assertEquals(h.group_key.call_args, call(i))
                self.assertEqual(h.on_new_key.call_args, call(i))

        h.group_key.reset_mock()
        h.on_new_key.reset_mock()
        for i in range(10):
            if i % 2 == 0:
                h[i] = i
                self.assertEquals(h.group_key.call_args, call(i))
        self.assertFalse(h.on_new_key.called)

        h.group_key.reset_mock()
        h.on_new_key.reset_mock()
        for i in range(10):
            if i % 2 == 0:
                self.assertEqual(h[i], i)
            else:
                self.assertEqual(h[i], 0)
            self.assertEquals(h.group_key.call_args, call(i))
        self.assertFalse(h.on_new_key.called)

    def test_update_entry(self):
        h = Histogram()

        h.group_key = MagicMock(wraps=h.group_key)
        h.on_new_key = MagicMock(wraps=h.on_new_key)
        for i in range(10):
            h.update_entry(i, i)
            self.assertEquals(h.group_key.call_args, call(i))
            self.assertEqual(h.on_new_key.call_args, call(i))

        for i in range(10):
            self.assertEqual(h[i], i)

        h.group_key.reset_mock()
        h.on_new_key.reset_mock()
        for i in range(10):
            h.update_entry(i, i)
            self.assertEquals(h.group_key.call_args, call(i))
        self.assertFalse(h.on_new_key.called)

        for i in range(10):
            self.assertEqual(h[i], i * 2)

    def test_distinct_update_entry(self):
        h = Histogram(update_value_func=lambda x, y, z: x + y + z)

        for i in range(10):
            h.update_entry(i, i, 1)

        for i in range(10):
            self.assertEqual(h[i], i + 1)

        for i in range(10):
            h.update_entry(i, i, 1)

        for i in range(10):
            self.assertEqual(h[i], (i + 1) * 2)

    def test_arrange_keys(self):
        h = Histogram()

        keys = [x for x in range(10)]
        self.assertEqual(h.arrange_keys(keys), keys)

    def test_keys(self):
        h = Histogram()

        h.arrange_keys = MagicMock(wraps=h.arrange_keys)

        keys = [1, 3, 4, 5, 63, 1323]
        for k in keys:
            h[k] = k
        self.assertEqual(h.keys(), keys)
        self.assertEqual(h.arrange_keys.call_count, 1)

        i = h.key_sequence()
        for k in keys:
            self.assertEqual(next(i), k)

    def test_group_key(self):
        h = Histogram()

        keys = [1, 3, 4, 5, 63, 1323]
        for k in keys:
            self.assertEqual(h.group_key(k), k)

    def test_len_bool(self):
        h = Histogram()

        self.assertEqual(len(h), 0)
        self.assertFalse(bool(h))
        keys = [1, 3, 4, 5, 63, 1323]
        for k in keys:
            h[k] = k
        self.assertEqual(len(h), 6)
        self.assertTrue(bool(h))

    def test_iter(self):
        h = Histogram()

        keys = [1, 3, 4, 5, 63, 1323]
        for k in keys:
            h[k] = k + 1

        i = 0
        for v in h:
            self.assertEqual(v, keys[i] + 1)
            i += 1

    def test_summarize(self):
        h = Histogram()

        keys = [1, 3, 4, 5, 63, 1323]
        for k in keys:
            h[k] = k

        s = NumericHistogramSummarizer()
        h.summarize(s)
        self.assertEqual(s.value, sum(keys))


if __name__ == '__main__':
    unittest.main()
