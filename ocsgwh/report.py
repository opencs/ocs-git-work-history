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
from datetime import date, timedelta
from collections import OrderedDict
from typing import Any, Callable
from .git.model import *

ONE_DAY_TIME_DELTA = timedelta(days=1)


class DiffSummary:
    def __init__(self, added: int = 0, deleted: int = 0) -> None:
        self.added = added
        self.deleted = deleted

    def update_with_entry(self, entry: GitDiffEntry):
        self.added += entry.added
        self.deleted += entry.deleted

    def update_with_diff(self, diff: GitDiff):
        for entry in diff:
            self.update_with_entry(entry)

    @property
    def changed(self):
        return self.added + self.deleted


def create_empty_histogram(start_date: date, end_date: date, value_class):
    """
    This class creates an empty histogram with a certain number of days.
    The parameter start_date: is the first day of the histogram, count is
    the number of days and value_class is the class that will hold the
    value (e.g.: DiffReport).
    """
    ret = OrderedDict()
    while start_date < end_date:
        ret[start_date] = value_class()
        start_date = start_date + ONE_DAY_TIME_DELTA
    return ret


class BaseHistogramBuilder:
    """
    This is the base class for all histogram builders that can process GitLog
    instances.

    The parameter default_value_creator must be a class or a function that will
    be used to create a new default entry for day in the histogram. This
    class constructor or function will be invoked without any parameters.
    """

    def __init__(self, start_date: date, end_date: date, default_value_creator) -> None:
        """
        """
        self._start_date = start_date
        self._end_date = end_date
        self._histogram = OrderedDict()
        while start_date < end_date:
            self.histogram[start_date] = default_value_creator()
            start_date = start_date + ONE_DAY_TIME_DELTA

    @property
    def start_date(self) -> date:
        return self._start_date

    @property
    def end_date(self) -> date:
        return self._end_date

    @property
    def histogram(self) -> OrderedDict:
        return self._histogram

    def update_entry(self, commit: GitCommit, current_value: Any) -> Any:
        """
        This method is called by scan() to update the day's entry with a new
        GitCommit. It receives the commit and the current_value and must return
        the new value after the update.

        Regardless of the ability to update current_value in place, this method
        must return the new value or the updated current_value.
        """
        raise NotImplemented('This method must be implemented by subclasses.')

    def scan(self, log: GitLog):
        for commit in log:
            d = commit.timestamp.date()
            if d >= self.start_date and d < self.end_date:
                self.histogram[d] = self.update_entry(
                    commit, self.histogram[d])


class DiffHistogramBuilder (BaseHistogramBuilder):

    def __init__(self, start_date: date, end_date: date) -> None:
        super(BaseHistogramBuilder, self).__init__(
            start_date, end_date, DiffSummary)

    def update_entry(self, commit: GitCommit, current_value: DiffSummary) -> DiffSummary:
        current_value.update_with_diff(commit.diff)
        return current_value


def create_author_diff_report(log: GitLog) -> list:
    """
    Creates a diff report for each user in the log. It returns a list of
    """
    tmp = {}
    for a in log.authors:
        tmp[a.email] = GitDiffBuilder()

    for commit in log:
        tmp[commit.author.email].add_diff(commit.diff)

    ret = []
    for a in log.authors:
        ret.append((a, tmp[a.email].build()))
    return ret


def basic_log_vars(log: GitLog):
    num_days = (log.max_date.date() - log.min_date.date()).days + 1
    commit_dates = set()
    for c in log:
        commit_dates.add(c.timestamp.date())
    days_with_commits = len(commit_dates)
    return {'start_date': log.min_date.date(), 'end_date': log.max_date.date(),
            'total_days': num_days, 'days_with_commits': days_with_commits,
            'days_with_commits_percent': (days_with_commits * 100) / float(num_days),
            'author_count': len(log.authors)}


def create_global_git_report(log: GitLog) -> list:
    b = GitDiffBuilder()

    basic_log = basic_log_vars(log)

    for c in log:
        b.add_diff(c.diff)
    diff = list(b.build())
    diff.sort(key=lambda x: x.file_name)
    added = 0
    deleted = 0
    added_only = 0
    for d in diff:
        added += d.added
        deleted += d.deleted
        if d.deleted == 0:
            added_only += 1

    mean_changes = float(added + deleted) / basic_log['days_with_commits']

    return {'diff': diff, 'total_added': added, 'total_deleted': deleted,
            'total_changed': added + deleted, 'mean_changes_per_day': mean_changes,
            'file_count': len(diff), 'added_only': added_only,
            **basic_log}
