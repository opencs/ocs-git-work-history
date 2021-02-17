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
from functools import total_ordering
from datetime import datetime, date
from enum import Enum, auto
from typing import OrderedDict


class GitAuthor:
    """
    This class implements a immutable Git author. It is always composed by an
    email and a name.

    Instances of this class are immutable
    """

    def __init__(self, email: str, name: str) -> None:
        self._email = email
        self._name = name
        self._rep = f'{self.name} <{self.email}>'

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    def __str__(self) -> str:
        return self._rep

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self._rep)

    def __eq__(self, o: object) -> bool:
        return self._rep == o._rep


class GitDiffEntry:
    """
    This class implements a Git diff entry. It contains the name of the
    file, the number of additons and deletions.

    Instances of this class are expected to be immutable.
    """

    def __init__(self, file_name: str, added: int, deleted: int, update_count: int = 0) -> None:
        self._file_name = file_name
        self._added = added
        self._deleted = deleted
        self._update_count = update_count

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

    @property
    def update_count(self) -> int:
        return self._update_count

    @property
    def diff_class(self) -> str:
        if self.deleted == 0:
            if self.added == 0:
                return 'empty'
            else:
                if self.update_count == 1:
                    return 'new'
                else:
                    return 'added'
        else:
            if self.added == self.deleted and self.update_count > 1:
                return 'removed'
            else:
                return 'normal'

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
        __slots__ = ('added', 'deleted', 'update_count')

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
            entry.update_count += 1
        else:
            entry = GitDiffBuilder.Accumulator()
            entry.added = added
            entry.deleted = deleted
            entry.update_count = 1
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
            entries.append(GitDiffEntry(
                f, entry.added, entry.deleted, entry.update_count))
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


@total_ordering
class GitAuthorName:
    """
    This class implements collection of authors that share the same
    normalized name.

    This class implements is both hashable and implements total ordering
    based on the value of the normalized name.
    """

    def __init__(self, name: str, authors: list) -> None:
        self._name = name
        self._authors = authors
        self._author_set = set(authors)

    @property
    def name(self) -> str:
        """
        Returns the normalized name of the author.
        """
        return self._name

    @property
    def authors(self) -> list:
        """
        Return a list of GitAuthor that shares the same normalized
        name.
        """
        return list(self._authors)

    def __contains__(self, author) -> bool:
        return author in self._author_set

    def __str__(self) -> str:
        s = self.name + ' ['
        for a in self.authors:
            s = s + str(a) + '; '
        return s + ']'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, o: object) -> bool:
        return self.name == o.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __lt__(self, o: object):
        return self.name < o.name


class ComparableGitAuthor:

    @staticmethod
    def normalize_name(name: str):
        """
        Normalizes a user name. It uses the following rules:

        * All parts of the names will be capitalized;
        * Multiple spaces between name parts will be replaced by a single space;
        * Starting and trailing spaces will be removed;

        For example, the string ' aLan MathisOn  Turing ' will become 'Alan Mathison Turing'.
        """
        return ' '.join(p.capitalize() for p in name.split()).strip()

    def __init__(self, author: GitAuthor) -> None:
        self.author = author
        self.email = author.email.strip().lower()
        self.name = ComparableGitAuthor.normalize_name(author.name)
        if not self.name:
            ValueError('The name cannot be empty.')
        self.parts = self.name.split(' ')

    def same_name(self, other) -> bool:
        return self.name == other.name

    def same_email(self, other) -> bool:
        return self.email == other.email

    def same_first_last(self, other) -> bool:
        return self.parts[0] == other.parts[0] and self.parts[-1] == other.parts[-1]

    def match(self, other) -> int:
        n = self.same_name(other)
        e = self.same_email(other)
        if e and n:
            # Name and email matches
            return 5
        elif e:
            # email only
            return 4
        if n:
            # Name only
            return 3
        elif self.same_first_last(other):
            # Partial match (first and last)
            return 2
        else:
            return 0

    def __hash__(self) -> int:
        return hash(self.author)

    def __eq__(self, other) -> bool:
        return self.author == other.author


class GitAuthorNameBuilder:

    def __init__(self, first: ComparableGitAuthor = None) -> None:
        self._authors = set()
        if first is not None:
            self._authors.add(first)

    def try_add(self, author: ComparableGitAuthor) -> bool:
        if not self._authors:
            self._authors.add(author)
            return True
        elif author in self._authors:
            return True
        else:
            for a in self._authors:
                if author.match(a) > 0:
                    self._authors.add(author)
                    return True
            return False

    def find_best_name(self):
        name = ''
        for a in self._authors:
            if len(a.name) > len(name):
                name = a.name
        return name

    def get_author_list(self):
        ret = []
        for a in self._authors:
            ret.append(a.author)
        ret.sort(key=lambda x: str(x))
        return ret

    def build(self) -> GitAuthorName:
        if not self._authors:
            raise ValueError('This instance has no associated authors.')

        name = self.find_best_name()
        authors = self.get_author_list()
        return GitAuthorName(name, authors)


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
        seen = set()
        builders = []
        for c in self._commits:
            if not c.author in seen:
                seen.add(c.author)
                found = False
                ca = ComparableGitAuthor(c.author)
                for candidate in builders:
                    if candidate.try_add(ca):
                        found = True
                        break
                if not found:
                    builders.append(GitAuthorNameBuilder(ca))
        self.authors = []
        for b in builders:
            self.authors.append(b.build())
        self.authors.sort(key=lambda x: x.name)

    def __len__(self) -> int:
        return len(self._commits)

    def __bool__(self) -> bool:
        return bool(self._commits)

    def __iter__(self):
        return iter(self._commits)

    def __getitem__(self, index: int) -> GitCommit:
        return self._commits[index]

    @ property
    def min_date(self) -> datetime:
        return self[0].timestamp

    @ property
    def max_date(self) -> datetime:
        return self[-1].timestamp

    def by_type(self, commit_type: GitCommitType):
        """
        Filters all commits of a given type.
        """
        return GitLog([c for c in self._commits if c.commit_type == commit_type])

    def by_authors(self, authors: list):
        """
        Filters all commits from a given user.
        """
        author_set = set(
            authors)  # Speed-up things by creating a set instead of a list
        return GitLog([c for c in self._commits if c.author in author_set])

    def by_author_name(self, author: GitAuthorName):
        """
        Filters all commits from a given user.
        """
        return GitLog([c for c in self._commits if c.author in author])

    def by_date(self, start_date: date, end_date: date):
        """
        Filters all commits between start(inclusive) and end_date(exclusive).
        """
        return GitLog([c for c in self._commits
                       if c.timestamp.date() >= start_date and c.timestamp.date() < end_date])
