#!/usr/bin/env python3
#
# Copyright (c) 2020-2026 James Cherti
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
from pathlib import Path
from typing import Any


class CacheFile:
    """
    Manage cache file operations.

    :param cache_filename: The path to the cache file.
    :type cache_filename: Path
    """

    def __init__(self, cache_filename: Path) -> None:
        """
        Initialize the cache file manager.

        :param cache_filename: The path to the cache file.
        :type cache_filename: Path
        """
        self.cache_filename: Path = cache_filename
        self._cache: dict[str, Any] = {}
        self._modified: bool = False

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.

        :param key: The key to set.
        :type key: str
        :param value: The value to store.
        :type value: Any
        """
        self._cache[key] = value
        self._modified = True

    def get(self, key: str, default: Any) -> Any:
        """
        Get a value from the cache.

        :param key: The key to retrieve.
        :type key: str
        :param default: The default value if the key is not found.
        :type default: Any
        :return: The cached value or the default.
        :rtype: Any
        """
        try:
            return self._cache[key]
        except KeyError:
            return default

    def load(self) -> None:
        """Load the cache from the file."""
        self.cache_filename.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.cache_filename.open(encoding="utf-8") as fhandler:
                data = json.load(fhandler)
                self._cache = data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            self._cache = {}
        self._modified = False

    def save(self) -> None:
        """Save the cache to the file."""
        if not self._modified:
            return

        self.cache_filename.parent.mkdir(parents=True, exist_ok=True)
        with self.cache_filename.open("w", encoding="utf-8") as fhandler:
            json.dump(self._cache, fhandler, indent=2)
        self._modified = False
