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
from datetime import date, datetime, timedelta
from collections import OrderedDict

ONE_DAY_DELTA = timedelta(days=1)


class DateSequenceIterator:
    """
    This class implements a date sequence iterator.
    """

    def __init__(self, start: date, end: date, step: timedelta = ONE_DAY_DELTA) -> None:
        """
        Creates a new instance of this class. The dates are generated 
        using ``start`` and ``end`` as boundaries and ``step`` as the
        increment.

        Since ``step`` may not be a divisor of the specified time interval, 
        the final date returned by this iterator is guaranteed to be less or
        equal to ``end``.

        Note: Specialized instances of ``date`` such as ``datetime`` can also be used.
        """
        self._curr = start
        self._end = end
        self._step = step

    def __next__(self) -> date:
        if self._curr > self._end:
            raise StopIteration()
        else:
            ret = self._curr
            self._curr = self._curr + self._step
            return ret

    def __iter__(self):
        return self


class HistogramSummarizer:
    def __init__(self) -> None:
        self._count = 0

    def update(self, value):
        pass


class NumericHistogramSummarizer:
    def __init__(self):
        self.value = 0

    def update(self, value):
        self.value += value


class Histogram:
    """
    This class implements a generic histogram. Each entry is identified by a key
    and a generic value.

    As a restriction, the ``key`` must be hashable and the ``value`` type
    is threated as immutable. However, it is up to the implementation of the
    update function to reuse the old instance to save new allocations.

    One important feature of this class is that, queries for values that have no
    data will always return ``create_value_func()``.
    """

    class Iterator:
        def __init__(self, source, key_seq) -> None:
            self.source = source
            self.key_seq = key_seq

        def __next__(self):
            return self.source[next(self.key_seq)]

    def __init__(self, create_value_func=lambda: 0, update_value_func=lambda a, b: a+b) -> None:
        """
        Creates a new instance of this class. By default the value is a number and the 
        update function is the sum of the values.

        The parameter ``create_value_func`` is a function that creates a new value (zero).

        The parameter ``update_value_func`` is a function that used to update the value.
        It takes at least two parameters, the old value and any other parameter you want.
        It returns the updated value that will replace the old one. For optimization reasons,
        it is allowed update old and return it.
        """
        self._create_value_func = create_value_func
        self._update_value_func = update_value_func
        self._entries = OrderedDict()

    def arrange_keys(self, l: list) -> list:
        """
        This method is called by keys() to sort the keys. Override it to
        change the sort behavior.

        By default, this method does nothing.
        """
        return l

    def keys(self) -> list:
        """
        Returns the set of keys in this instance. Override this method
        to customize the key set.

        By default, it returns the list of keys in order of insertion like
        ``collections.OrderedDict`` does.
        """
        return self.arrange_keys([k for k in self._entries])

    def key_sequence(self):
        """
        Returns a sequence generator that returns the keys inside this
        histogram. It is called by the implementation of iterator to 
        determine the order of iteration.

        Override this method to change its behavior.

        By default, it returns ``iter(self.keys())``.
        """
        return iter(self.keys())

    def group_key(self, key):
        """
        This method is called by read/write operators to group the keys
        into groups. Override this method to change the key grouping
        behavior.

        By default, it returns the key itself.
        """
        return key

    def on_new_key(self, key):
        """
        This is a callback that is called to report that a new
        key has been added.

        By default, it does nothing.
        """
        pass

    def update_entry(self, key, *args):
        """
        Updates the key using the function ``update_value_func``. All
        parameters in ``*args`` are passed directly to the update function.

        It will create new keys if the key does not exist.
        """
        key = self.group_key(key)
        if key in self._entries:
            old = self._entries[key]
        else:
            old = self._create_value_func()
        self.__setitem_core(key, self._update_value_func(old, *args))

    def __bool__(self):
        return bool(self._entries)

    def __len__(self) -> int:
        """
        Returns the number of entries in the key list.

        By default, it returns len(self.keys()). Subclasses are encoraged
        to override this method if they have better implementations of this
        method.
        """
        return len(self.keys())

    def __getitem__(self, key):
        key = self.group_key(key)
        if key in self._entries:
            return self._entries[key]
        else:
            return self._create_value_func()

    def __setitem__(self, key, value):
        self.__setitem_core(self.group_key(key), value)

    def __setitem_core(self, group_key, value):
        if group_key not in self._entries:
            self.on_new_key(group_key)
        self._entries[group_key] = value

    def __iter__(self):
        return Histogram.Iterator(self, self.key_sequence())

    def summarize(self, summarizer: HistogramSummarizer):
        """
        This method creates a instance of value that updates the
        value using the specified sum function. This function must
        take 2 parameters, the old value and a value and returns the
        updated value.
        """
        for v in self._entries.values():
            summarizer.update(v)


class DailyHistogram(Histogram):
    """
    This is a specialized version of the Histogram class that works with
    days as its basic grouping unit.

    As such, it can be updated with keys being both ``date`` and ``datetime``
    instances. Furthermore, the scan
    """

    def __init__(self, create_value_func=lambda: 0, update_value_func=lambda a, b: a+b) -> None:
        super().__init__(create_value_func, update_value_func)
        self._min_date = date.max
        self._max_date = date.min

    @property
    def min_date(self) -> date:
        return self._min_date

    @property
    def max_date(self) -> date:
        return self._max_date

    def on_new_key(self, key):
        self._min_date = min(self._min_date, key)
        self._max_date = max(self._max_date, key)

    def keys(self) -> list:
        return [x for x in self.key_sequence()]

    def group_key(self, key):
        if isinstance(key, datetime):
            return key.date()
        elif isinstance(key, date):
            return key
        else:
            raise ValueError(
                'The key must be an instance of date or datetime.')

    def key_sequence(self):
        return DateSequenceIterator(self.min_date, self.max_date, ONE_DAY_DELTA)

    def __len__(self) -> int:
        if self._entries:
            return (self.max_date - self.min_date).days + 1
        else:
            return 0
