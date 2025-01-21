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
"""Readline manager."""


import logging
import readline
import sys
from pathlib import Path
from typing import List, Optional, Set, Union


class ReadlineSimpleCompleter:
    def __init__(self, options: List[str]):
        """Initialize with a sorted list of options."""
        self.complete_with = sorted(options)
        self.matches: List[str] = []

    def complete(self, _, state: int) -> Optional[str]:
        """Return the next possible completion for 'text'."""
        if state == 0:
            orig_line = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()
            being_completed = orig_line[begin:end]
            self.matches = [string for string in self.complete_with
                            if string.startswith(being_completed)]

        return self.matches[state] if state < len(self.matches) else None


class ReadlineManager:
    def __init__(self, history_file: Union[str, Path, None] = None):
        """Manage readline settings, history, and input."""
        self.history_file = Path(history_file) if history_file else None
        self.keywords: Set[str] = set()

    def _init_history(self):
        """Initialize readline history from the specified file."""
        if self.history_file and self.history_file.exists():
            readline.read_history_file(self.history_file)
            self._load_keywords_from_history()
            logging.debug("[DEBUG] History loaded")

    def _load_keywords_from_history(self):
        """
        Load and extract unique keywords from the history file for completion.
        """
        if self.history_file and self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as file:
                lines = file.readlines()

            for line in lines:
                self.keywords |= set(line.strip().split())

    def _save_history(self):
        """Save the current readline history to the specified file."""
        if self.history_file:
            logging.debug("[DEBUG] History saved")
            readline.write_history_file(self.history_file)

    def readline_input(self, prompt: str,
                       default: str = "",
                       required: bool = False,
                       complete_with: Union[List[str], None] = None,
                       quit_on_eof: bool = True,
                       quit_on_ctrlc: bool = True) -> str:
        """
        Prompt for input with optional readline autocompletion and command
        history saving.
        """
        self._init_history()
        all_keywords = self.keywords | \
            set(complete_with if complete_with else {})
        logging.debug("[DEBUG] Keywords: %s", str(all_keywords))
        completer = ReadlineSimpleCompleter(list(all_keywords) or [])
        previous_completer = readline.get_completer()
        try:
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            if default:
                prompt += f" (default: {default})"

            save_history = False
            try:
                while True:
                    try:
                        value = input(prompt)
                        if not value and required and default is None:
                            print("Error: a value is required")
                            continue

                        save_history = True
                        break
                    except EOFError:
                        if quit_on_eof:
                            print()
                            print("Interrupted.")
                            sys.exit(0)
                    except KeyboardInterrupt:
                        if quit_on_ctrlc:
                            print()
                            print("Interrupted.")
                            sys.exit(0)
            finally:
                if save_history and self.history_file:
                    self._save_history()

            return default if value == "" else value
        finally:
            readline.set_completer(previous_completer)
