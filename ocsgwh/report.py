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
import pygal
from .historgram import DailyHistogram, DateSequenceIterator, ONE_WEEK_DELTA, find_previous_sunday, WeeklyHistogram
from .git.model import *

ONE_DAY_TIME_DELTA = timedelta(days=1)


class DiffSummaryValue:
    def __init__(self, added: int = 0, deleted: int = 0) -> None:
        self.added = added
        self.deleted = deleted
        self.update_count = 0

    @property
    def changed(self):
        return self.added + self.deleted

    def new():
        """
        Creates a new instace with all properties set to 0.

        This static method was designed to be used with ``Histogram`` as ``create_value_func``.
        """
        return DiffSummaryValue()

    @staticmethod
    def update(old, v):
        """
        Updates the old (``DiffSummaryValue``) entry with another intance of 
        ``DiffSummaryValue``, ``GitDiffEntry`` or ``GitDiff``. It always returns old.

        Each call to this method increments ``update_count`` by one.

        This static method was designed to be used with ``Histogram`` as ``update_value_func``.
        """
        old.update_count += 1
        if isinstance(v, DiffSummaryValue) or isinstance(v, GitDiffEntry):
            old.added += v.added
            old.deleted += v.deleted
        elif isinstance(v, GitDiff):
            for d in v:
                old.added += d.added
                old.deleted += d.deleted
        else:
            raise ValueError('')
        return old


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


def generate_histogram_image(h: DailyHistogram, start: date, end: date):
    labels = [x for x in DateSequenceIterator(start, end)]
    added = []
    deleted = []
    commits = []
    for l in labels:
        v = h[l]
        added.append(v.added)
        deleted.append(v.deleted)
        commits.append(v.update_count)

    line_chart = pygal.Bar(x_label_rotation=90, height=800, width=1600)
    line_chart.title = f'Daily activity from {start} to {end}'
    line_chart.x_labels = map(str, labels)
    line_chart.add('Added', added)
    line_chart.add('Deleted', deleted)
    line_chart.add('Commits', commits)
    return (line_chart.title, line_chart.render_data_uri())


FOUR_WEEKS_DELTA = timedelta(weeks=4)


def generate_histogram(log: GitLog) -> str:

    h = DailyHistogram(create_value_func=DiffSummaryValue.new,
                       update_value_func=DiffSummaryValue.update)
    # Compute the histogram
    for commit in log:
        if commit.diff:
            h.update_entry(commit.timestamp, commit.diff)
    histograms = []
    start = find_previous_sunday(h.min_date)
    while start < h.max_date:
        end = start + ONE_WEEK_DELTA
        histograms.append(
            generate_histogram_image(h, start, end - ONE_DAY_TIME_DELTA))
        start = end

    return histograms


def generate_weakly_histogram(log: GitLog) -> str:

    h = WeeklyHistogram(create_value_func=DiffSummaryValue.new,
                        update_value_func=DiffSummaryValue.update)
    # Compute the histogram
    for commit in log:
        if commit.diff:
            h.update_entry(commit.timestamp, commit.diff)

    labels = h.keys()
    added = []
    deleted = []
    commits = []
    for l in labels:
        v = h[l]
        added.append(v.added)
        deleted.append(v.deleted)
        commits.append(v.update_count)

    line_chart = pygal.Bar(x_label_rotation=90, height=800, width=1600)
    line_chart.title = f'Weekly activity from {h.min_date} to {h.max_date}'
    line_chart.x_labels = map(str, labels)
    line_chart.add('Added', added)
    line_chart.add('Deleted', deleted)
    line_chart.add('Commits', commits)
    return (line_chart.title, line_chart.render_data_uri())


def create_global_git_report(log: GitLog) -> list:
    b = GitDiffBuilder()

    basic_log = basic_log_vars(log)

    merges = 0
    for c in log:
        b.add_diff(c.diff)
        if c.commit_type == GitCommitType.MERGE:
            merges += 1

    diff = list(b.build())
    diff.sort(key=lambda x: x.file_name)
    added = 0
    deleted = 0
    added_only = 0
    renames = 0
    binaries = 0
    for d in diff:
        added += d.added
        deleted += d.deleted
        if d.deleted == 0 and d.update_count == 1:
            added_only += 1
        if d.rename:
            renames += 1
        if d.binary:
            binaries += 1

    histo = generate_histogram(log)
    weekly_histo = generate_weakly_histogram(log)
    mean_changes = float(added + deleted) / basic_log['days_with_commits']

    return {'diff': diff, 'total_added': added, 'total_deleted': deleted,
            'total_changed': added + deleted, 'mean_changes_per_day': mean_changes,
            'file_count': len(diff), 'added_only': added_only,
            'merges': merges, 'renames': renames, 'binaries': binaries, 'histogram': histo,
            'weekly_histo': weekly_histo, **basic_log}
