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
from pathlib import Path


class ReadlineSimpleCompleter:
    def __init__(self, options: list[str]):
        """Initialize with a sorted list of options."""
        self.complete_with = sorted(options)
        self.matches: list[str] = []

    def complete(self, _, state: int):
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
    def __init__(self, history_file=None,
                 history_length=-1):
        """Manage readline settings, history, and input."""
        self.history_file = Path(history_file) if history_file else None
        self.keywords = set()
        self.history_length = history_length
        # self.history = []
        self._init_history()

    def _init_history(self):
        """Initialize readline history from the specified file."""
        if not (self.history_file and self.history_file.exists()):
            return

        if self.history_length >= 0:
            readline.set_history_length(self.history_length)

        # History
        self.read_history_file()

        # Keywords
        # if self.history_file and self.history_file.exists():
        #     with open(self.history_file, "r", encoding="utf-8") as file:
        #         self.history = file.readlines()
        #
        #     for line in self.history:
        #         self.keywords |= set(line.strip().split())

        logging.debug("[DEBUG] History loaded")

    def append_to_history(self, string):
        # self.history.append(string)
        readline.add_history(string)

        # # Truncate history
        # if self.history_length >= 0 \
        #         and len(self.history) > self.history_length:
        #     self.history = self.history[:-self.history_length]
        #     with open(self.history_file, "w", encoding="utf-8") as fhandler:
        #         for line in self.history:
        #             fhandler.write(f"{line}\n")
        # else:
        #     with open(self.history_file, "a", encoding="utf-8") as fhandler:
        #         fhandler.write(f"{string}\n")

    def read_history_file(self):
        """Read the current readline history to the specified file."""
        if self.history_file:
            readline.read_history_file(self.history_file)

    def save_history_file(self):
        """Save the current readline history to the specified file."""
        if self.history_file:
            logging.debug("[DEBUG] History saved")
            readline.write_history_file(self.history_file)

    def readline_input(self, prompt: str,
                       default: str = "",
                       required: bool = False,
                       complete_with=None) -> str:
        """
        Prompt for input with optional readline autocompletion and command
        history saving.

        :complete_with: A list of strings to complete with.
        """
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
                    value = input(prompt)
                    if not value and required and default is None:
                        print("Error: a value is required")
                        continue

                    save_history = True
                    break
            finally:
                if save_history and self.history_file:
                    self.save_history_file()

            return default if value == "" else value
        finally:
            readline.set_completer(previous_completer)
