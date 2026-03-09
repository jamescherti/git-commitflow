#!/usr/bin/env python
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
"""Git Commitflow helpers."""


import os
import re
from pathlib import Path
from typing import Union


def replace_home_with_tilde(path: Union[Path, str]) -> str:
    """
    Replace the home directory with '~'.

    :param path: The path to process.
    :type path: Path
    :return: The path string with the home directory replaced by '~'.
    :rtype: str
    """
    path = Path(path)
    try:
        return "~/" + str(path.relative_to(Path.home()))
    except ValueError:
        return str(path)


def remove_matching_filenames(filenames: list[str],
                              patterns: list[str]) -> list[str]:
    """
    Remove filenames that match any of the given regex patterns.

    :param filenames: A list of filenames to filter.
    :param patterns: A list of regex patterns to match filenames against.
    :return: A list of filenames that do not match any of the patterns.
    """
    compiled_patterns = [re.compile(pattern) for pattern in patterns]
    filtered_filenames = [filename for filename in filenames
                          if not any(pattern.match(os.path.basename(filename))
                                     for pattern in compiled_patterns)]
    return filtered_filenames
