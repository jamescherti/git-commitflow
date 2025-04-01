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
"""Git commit and push helper."""


import logging
import os
import subprocess
import sys

import colorama

from .git_commitflow import GitCommitFlow


def git_commitflow_cli():
    """The git-commitflow command-line interface."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format="%(asctime)s %(name)s: %(message)s")
    colorama.init()

    try:
        import platform  # pylint: disable=import-outside-toplevel
        if os.name == "nt":
            import msvcrt  # pylint: disable=import-outside-toplevel

            # Check if there's input in the buffer
            while msvcrt.kbhit():
                # Read and discard one character at a time
                msvcrt.getch()
        elif os.name == "posix" or platform.system() in ["Linux", "Darwin"]:
            # For Unix-like systems, check if there's any pending input in
            # stdin without blocking
            import select  # pylint: disable=import-outside-toplevel

            # Check if there is any pending input in stdin without blocking
            # If input is available, flush the stdin buffer
            stdin, _, _ = select.select([sys.stdin], [], [], 0)
            if stdin:
                if sys.stdin.isatty():
                    # pylint: disable=import-outside-toplevel
                    from termios import TCIFLUSH, tcflush

                    # Flush the input buffer
                    tcflush(sys.stdin.fileno(), TCIFLUSH)
                else:
                    # Read and discard input (in chunks)
                    sys.stdin.read(1024)
    except ImportError:
        pass

    try:
        GitCommitFlow().main()
    except subprocess.CalledProcessError as main_proc_err:
        print(f"Error: {main_proc_err}")
    except KeyboardInterrupt:
        print()
