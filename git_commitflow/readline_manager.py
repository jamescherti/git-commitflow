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
"""Readline manager."""

import logging
import readline
from pathlib import Path
from typing import Any, Optional


class ReadlineSimpleCompleter:
    """
    Simple readline completer.
    """

    def __init__(self, options: list[str]) -> None:
        """
        Initialize with a sorted list of options.

        :param options: list of completion options.
        :type options: list[str]
        """
        self.complete_with: list[str] = sorted(options)
        self.matches: list[str] = []

    def complete(self, _: Any, state: int) -> Optional[str]:
        """
        Return the next possible completion for 'text'.

        :param state: The completion state index.
        :type state: int
        :return: The matching string or None.
        :rtype: Optional[str]
        """
        if state == 0:
            orig_line: str = readline.get_line_buffer()
            begin: int = readline.get_begidx()
            end: int = readline.get_endidx()
            being_completed: str = orig_line[begin:end]
            self.matches = [string for string in self.complete_with
                            if string.startswith(being_completed)]

        return self.matches[state] if state < len(self.matches) else None


class ReadlineManager:
    """
    Readline manager for history and autocompletion.
    """

    def __init__(self, history_file: Optional[Path] = None,
                 history_length: int = -1) -> None:
        """
        Manage readline settings, history, and input.

        :param history_file: Path to the history file.
        :type history_file: Optional[Path]
        :param history_length: The length of history to retain.
        :type history_length: int
        """
        self.history_file: Optional[Path] = Path(
            history_file) if history_file else None
        self.keywords: set[str] = set()
        self.history_length: int = history_length
        # self.history = []
        self._init_history()

    def _init_history(self) -> None:
        """
        Initialize readline history from the specified file.
        """
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

    def append_to_history(self, string: str) -> None:
        """
        Append string to history.

        :param string: The string to append.
        :type string: str
        """
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

    def read_history_file(self) -> None:
        """
        Read the current readline history to the specified file.
        """
        if self.history_file:
            readline.read_history_file(str(self.history_file))

    def save_history_file(self) -> None:
        """
        Save the current readline history to the specified file.
        """
        if self.history_file:
            logging.debug("[DEBUG] History saved")
            readline.write_history_file(str(self.history_file))

    def readline_input(self, prompt: str,
                       default: str = "",
                       required: bool = False,
                       complete_with: Optional[list[str]] = None) -> str:
        """
        Prompt for input with optional readline autocompletion and command
        history saving.

        :param prompt: The prompt string.
        :type prompt: str
        :param default: Default return value.
        :type default: str
        :param required: Whether input is required.
        :type required: bool
        :param complete_with: A list of strings to complete with.
        :type complete_with: Optional[list[str]]
        :return: The input string.
        :rtype: str
        """
        all_keywords: set[str] = self.keywords | \
            set(complete_with if complete_with else [])
        logging.debug("[DEBUG] Keywords: %s", str(all_keywords))
        completer: ReadlineSimpleCompleter = ReadlineSimpleCompleter(
            list(all_keywords) or [])
        previous_completer: Any = readline.get_completer()
        try:
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            if default:
                prompt += f" (default: {default})"

            save_history: bool = False
            try:
                while True:
                    value: str = input(prompt)
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
