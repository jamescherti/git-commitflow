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
"""Tests for git-commitflow cache file handling."""

import os
import stat
from pathlib import Path

import pytest

from git_commitflow.cache_file import CacheFile


def test_save_unwritable_file_warns_instead_of_crashing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Saving to a read-only cache file warns instead of raising."""
    cache_file = tmp_path / "repo-data.json"
    cache_file.write_text("{}", encoding="utf-8")
    os.chmod(cache_file, stat.S_IREAD)

    cache = CacheFile(cache_file)
    cache.set("git_push_commit_refs", {})
    cache.save()  # Must warn on stderr instead of raising PermissionError.

    assert "repo-data.json" in capsys.readouterr().err
