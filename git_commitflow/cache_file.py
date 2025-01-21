#!/usr/bin/env python
#
# Copyright (c) 2020-2025 James Cherti
# URL: https://github.com/jamescherti/git-commitflow
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
#
"""Cache file."""


import json
from typing import Any


class CacheFile:
    def __init__(self, cache_filename):
        self.cache_filename = cache_filename
        self._cache = {}
        self._modified = True

    def set(self, key: str, value: str):
        try:
            self._cache[key]
        except KeyError:
            self._cache[key] = {}

        self._cache[key] = value
        self._modified = True

    def get(self, key: str, default: Any) -> Any:
        try:
            return self._cache[key]
        except KeyError:
            return default

    def load(self):
        self.cache_filename.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.cache_filename, "r", encoding="utf-8") as fhandler:
                self._cache = dict(json.load(fhandler))
        except FileNotFoundError:
            return

    def save(self):
        if not self._modified:
            return

        with open(self.cache_filename, "w", encoding="utf-8") as fhandler:
            json.dump(self._cache, fhandler, indent=2)
