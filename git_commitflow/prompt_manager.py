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
"""Prompt manager using prompt_toolkit."""

import logging
from pathlib import Path

from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name
from prompt_toolkit.shortcuts import CompleteStyle


class _PromptHistory(InMemoryHistory):
    """In-memory prompt history that ignores slash commands."""

    def append_string(self, string: str) -> None:
        """
        Append a string to history unless it starts with '/'.

        :param string: The input string to store.
        :type string: str
        """
        if string and not string.startswith("/"):
            super().append_string(string)


class PromptManager:
    """Prompt manager for history and autocompletion using prompt_toolkit."""

    def __init__(
        self, history_file: Path | None = None, history_length: int = -1
    ) -> None:
        """
        Manage prompt_toolkit settings, history, and input.

        :param history_file: Path to the history file.
        :type history_file: Optional[Path]
        :param history_length: The length of history to retain.
        :type history_length: int
        """
        self.history_file: Path | None = Path(history_file) if history_file else None
        self.keywords: set[str] = set()
        self.history_length: int = history_length
        self.history: _PromptHistory = _PromptHistory()
        self._init_history()

    @staticmethod
    def _create_key_bindings() -> KeyBindings:
        """Create key bindings for Alt+hjkl alongside default arrow keys."""
        kb = KeyBindings()

        @kb.add("escape", "h")
        def _left(event: KeyPressEvent) -> None:
            get_by_name("backward-char").call(event)

        @kb.add("escape", "l")
        def _right(event: KeyPressEvent) -> None:
            get_by_name("forward-char").call(event)

        @kb.add("escape", "k")
        def _up(event: KeyPressEvent) -> None:
            event.current_buffer.auto_up(count=event.arg)

        @kb.add("escape", "j")
        def _down(event: KeyPressEvent) -> None:
            event.current_buffer.auto_down(count=event.arg)

        return kb

    def _init_history(self) -> None:
        """Initialize prompt history from the specified file."""
        if not (self.history_file and self.history_file.exists()):
            return

        self.read_history_file()
        logging.debug("[DEBUG] History loaded")

    def append_to_history(self, string: str) -> None:
        """
        Append string to history.

        :param string: The string to append.
        :type string: str
        """
        self.history.append_string(string)

    def read_history_file(self) -> None:
        """Read the prompt history from the specified file."""
        if self.history_file and self.history_file.exists():
            try:
                with self.history_file.open(
                    encoding="utf-8", errors="replace"
                ) as fhandler:
                    lines: list[str] = [
                        line.rstrip("\r\n")
                        for line in fhandler
                        if line.rstrip("\r\n") and not line.startswith("/")
                    ]
            except OSError:
                return

            if self.history_length >= 0:
                lines = lines[-self.history_length :]

            self.history = _PromptHistory(lines)

    def save_history_file(self) -> None:
        """Save the current prompt history to the specified file."""
        if self.history_file:
            logging.debug("[DEBUG] History saved")
            strings: list[str] = [
                item
                for item in self.history.get_strings()
                if item and not item.startswith("/")
            ]
            if self.history_length >= 0:
                strings = strings[-self.history_length :]

            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with self.history_file.open("w", encoding="utf-8") as fhandler:
                for line in strings:
                    fhandler.write(f"{line}\n")

    def prompt_input(
        self,
        prompt: str,
        default: str = "",
        required: bool = False,
        complete_with: list[str] | None = None,
    ) -> str:
        """
        Prompt for input with optional autocompletion and command history saving.

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
        all_keywords: set[str] = self.keywords | set(complete_with or [])
        logging.debug("[DEBUG] Keywords: %s", str(all_keywords))
        completer: WordCompleter = WordCompleter(sorted(all_keywords), WORD=True)

        if default:
            prompt += f" (default: {default})"

        save_history: bool = False
        try:
            while True:
                value: str = pt_prompt(
                    prompt,
                    history=self.history,
                    completer=completer,
                    complete_while_typing=False,
                    complete_style=CompleteStyle.READLINE_LIKE,
                    key_bindings=self._create_key_bindings(),
                )
                if not value and required and not default:
                    print("Error: a value is required")
                    continue

                if value and not value.startswith("/"):
                    save_history = True

                break
        finally:
            if save_history and self.history_file:
                self.save_history_file()

        return default if value == "" else value
