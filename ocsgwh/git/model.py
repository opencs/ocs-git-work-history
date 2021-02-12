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
from datetime import date, datetime


class GitAuthor:
    """
    This class implements a immutable Git author. It is always composed by an
    email (the actual key) and a name.

    Two authors are considered the same if and only if their emails are the same.
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


class GitDiffEntry:
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

    def same(self, other):
        return isinstance(other, GitDiffEntry) and self.file_name == other.file_name

    def merge(self, other):
        if self.same(other):
            return GitDiffEntry(self.file_name, self.added + other.added, self.deleted + other.deleted)
        else:
            raise ValueError(
                "The file names don't match.")


class GitDiff:
    def __init__(self) -> None:
        self._entries = dict()
        self._added = 0
        self._deleted = 0

    def add(self, entry: GitDiffEntry):
        self._added = self._added + entry.added
        self._deleted = self._deleted + entry.deleted
        if not entry.file_name in self._entries:
            self._entries[entry.file_name] = entry
        else:
            prev = self._entries[entry.file_name]
            self._entries[entry.file_name] = prev.merge(entry)

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
        return iter(self._entries.values())

    def __getitem__(self, file_name: str) -> GitDiffEntry:
        return self._entries[file_name]

    def merge(self, other):
        ret = GitDiff()
        for d in self:
            ret.add(d)
        for d in other:
            ret.add(d)
        return ret


class GitCommit:
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
    def merge(self) -> bool:
        return len(self.parents) != 1
