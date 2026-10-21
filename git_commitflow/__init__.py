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
"""Git commit and push helper."""

import logging
import subprocess
import sys
from pathlib import Path

try:
    import colorama

    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False


from .git_commitflow import GitCommitFlow


def git_commitflow_cli() -> None:
    """Run the git-commitflow command-line interface."""
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(name)s: %(message)s",
    )

    # Optional feature: setproctitle
    try:
        # pylint: disable=import-outside-toplevel
        from setproctitle import setproctitle  # noqa: PLC0415

        setproctitle(Path(sys.argv[0]).name)  # type: ignore
    except ImportError:
        # Optional dependency 'setproctitle' is not installed.
        pass

    if HAS_COLORAMA:
        colorama.init()

    try:
        GitCommitFlow().main()
    except subprocess.CalledProcessError as main_proc_err:
        print(f"Error: {main_proc_err}", file=sys.stderr)
        sys.exit(main_proc_err.returncode or 1)
    except KeyboardInterrupt:
        print(file=sys.stderr)
        sys.exit(130)
