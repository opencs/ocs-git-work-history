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
from datetime import datetime, date
from enum import Enum, auto


class GitAuthor:
    """
    This class implements a immutable Git author. It is always composed by an
    email (the actual key) and a name.

    Two authors are considered the same if and only if their emails are the same.

    Instances of this class are expected to be immutable.
    """

    def __init__(self, email: str, name: str) -> None:
        self._email = email
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    def same(self, o: object) -> bool:
        return self._email == o._email

    def __str__(self) -> str:
        return f'{self.name} <{self.email}>'

    def __repr__(self) -> str:
        return str(self)


class GitDiffEntry:
    """
    This class implements a Git diff entry. It contains the name of the
    file, the number of additons and deletions.

    Instances of this class are expected to be immutable.
    """

    def __init__(self, file_name: str, added: int, deleted: int) -> None:
        self._file_name = file_name
        self._added = added
        self._deleted = deleted

    @property
    def file_name(self) -> str:
        return self._file_name

    @property
    def added(self) -> int:
        return self._added

    @property
    def deleted(self) -> int:
        return self._deleted

    @property
    def changed(self) -> int:
        return self.added + self.deleted

    def __eq__(self, o: object) -> bool:
        return self.file_name == o.file_name and self.added == o.added and self.deleted == o.deleted


class GitDiff:
    """
    This class implements the diff set of a given commit. It contains 0 or more git diff
    entries.

    Instances of this class are expected to be immutable.
    """

    def __init__(self, entries: list) -> None:
        self._entries = list(entries)
        self._added = 0
        self._deleted = 0
        for entry in entries:
            self._added += entry.added
            self._deleted += entry.deleted

    @property
    def added(self) -> int:
        return self._added

    @property
    def deleted(self) -> int:
        return self._deleted

    @property
    def changed(self) -> int:
        return self.added + self.deleted

    def __bool__(self) -> bool:
        return bool(self._entries)

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def __getitem__(self, index: int) -> GitDiffEntry:
        return self._entries[index]


class GitDiffBuilder:
    """
    This class is a builder for ``GitDiff`` instances.
    """
    class Accumulator:
        __slots__ = ('added', 'deleted')

    def __init__(self) -> None:
        self._entries = dict()

    def reset(self):
        """
        Resets this builder. It is equivalent to create a new instance.

        Returns: self.
        """
        self._entries.clear()
        return self

    def add_entry(self, file_name: str, added: int, deleted: int) -> object:
        """
        Adds a diff entry. It will update existing file statistics if it is
        already registered.

        Returns: self.
        """
        if file_name in self._entries:
            entry = self._entries[file_name]
            entry.added += added
            entry.deleted += deleted
        else:
            entry = GitDiffBuilder.Accumulator()
            entry.added = added
            entry.deleted = deleted
            self._entries[file_name] = entry
        return self

    def add_diff_entry(self, entry: GitDiffEntry) -> object:
        """
        Adds a diff entry but uses a ``GitDiffEntry`` as its input.

        Returns: self.
        """
        return self.add_entry(entry.file_name, entry.added, entry.deleted)

    def add_diff(self, diff: GitDiff) -> object:
        """
        Adds all entries inside another ``GitDiff`` instance. It is useful to
        merge 2 or more ``GitDiff`` instances.

        Returns: self.
        """
        for entry in diff:
            self.add_diff_entry(entry)
        return self

    def build(self) -> GitDiff:
        """
        Builds a new ``GitDiff`` instance based on the current state of 
        this builder.

        It is important to notice that calls to this method doesn't reset
        its internal state thus multiple clones
        """
        entries = []
        files = list(self._entries)
        files.sort()
        for f in files:
            entry = self._entries[f]
            entries.append(GitDiffEntry(f, entry.added, entry.deleted))
        return GitDiff(entries)


class GitCommitType(Enum):
    ROOT = auto()
    NORMAL = auto()
    MERGE = auto()


class GitCommit:
    """
    This class implements the complete Git commit information.

    Instances of this class are expected to be immutable.
    """

    def __init__(self, id, parents: list, timestamp: datetime, author: GitAuthor, diff: GitDiff) -> None:
        self._id = id
        self._parents = parents
        self._timestamp = timestamp
        self._author = author
        self._diff = diff

    @property
    def id(self) -> str:
        return self._id

    @property
    def parents(self) -> list:
        return self._parents

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def author(self) -> GitAuthor:
        return self._author

    @property
    def diff(self) -> GitDiff:
        return self._diff

    @property
    def commit_type(self) -> GitCommitType:
        """
        Returns the type of the commit. It uses the number of parents
        to determine the type of the commit.
        """
        return (
            GitCommitType.ROOT,
            GitCommitType.NORMAL,
            GitCommitType.MERGE)[min(len(self.parents), 2)]


class GitLog:
    """
    This class implements a Git log. It gets a list of ``GitCommit``
    instances and extracts some useful statistics from it.

    Instances of this class are expected to be immutable.
    """
    # TODO: The implementation of this class may be optimized in the future.

    def __init__(self, commits: list) -> None:
        self._commits = list(commits)
        self._update()

    def _update(self):
        self._commits.sort(key=lambda x: x.timestamp)
        authors = {}
        for c in self._commits:
            authors[c.author.email] = c.author
        self.authors = list(authors.values())
        self.authors.sort(key=lambda x: x.email)

    def __len__(self) -> int:
        return len(self._commits)

    def __bool__(self) -> bool:
        return bool(self._commits)

    def __iter__(self):
        return iter(self._commits)

    def __getitem__(self, index: int) -> GitCommit:
        return self._commits[index]

    @property
    def min_date(self) -> datetime:
        return self[0].timestamp

    @property
    def max_date(self) -> datetime:
        return self[-1].timestamp

    def by_type(self, commit_type: GitCommitType):
        """
        Filters all commits of a given type.
        """
        return GitLog([c for c in self._commits if c.commit_type == commit_type])

    def by_author(self, author_email: str):
        """
        Filters all commits from a given user.
        """
        return GitLog([c for c in self._commits if c.author.email == author_email])

    def by_date(self, start_date: date, end_date: date):
        """
        Filters all commits between start(inclusive) and end_date(exclusive).
        """
        return GitLog([c for c in self._commits
                       if c.timestamp.date() >= start_date and c.timestamp.date() < end_date])
