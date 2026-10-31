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
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.data_structures import Point
from prompt_toolkit.formatted_text import ANSI, FormattedText, to_formatted_text
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name
from prompt_toolkit.layout.containers import (
    Float,
    FloatContainer,
    HSplit,
    Window,
)
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.shortcuts import CompleteStyle


class _PromptHistory(InMemoryHistory):
    """In-memory prompt history that ignores slash commands."""

    def append_string(self, string: str) -> None:
        """
        Append a string to history unless it starts with '/'.

        :param string: The input string to store.
        :type string: str
        """
        string = string.strip()
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

        @kb.add("escape", "H")
        def _word_left(event: KeyPressEvent) -> None:
            get_by_name("backward-word").call(event)

        @kb.add("escape", "L")
        def _word_right(event: KeyPressEvent) -> None:
            get_by_name("forward-word").call(event)

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
                        line.strip()
                        for line in fhandler
                        if line.strip() and not line.strip().startswith("/")
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
                item.strip()
                for item in self.history.get_strings()
                if item.strip() and not item.strip().startswith("/")
            ]
            if self.history_length >= 0:
                strings = strings[-self.history_length :]

            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with self.history_file.open("w", encoding="utf-8") as fhandler:
                for line in strings:
                    fhandler.write(f"{line}\n")

    def _prompt_with_diff(
        self,
        prompt: str,
        default: str,
        required: bool,
        completer: WordCompleter,
        diff_text: str,
    ) -> str:
        """
        Display a full-screen split-pane diff viewer and input prompt.

        :param prompt: The prompt string.
        :type prompt: str
        :param default: Default return value.
        :type default: str
        :param required: Whether input is required.
        :type required: bool
        :param completer: Configured WordCompleter instance.
        :type completer: WordCompleter
        :param diff_text: ANSI-colored diff string to render.
        :type diff_text: str
        :return: The entered string.
        :rtype: str
        """
        clean_diff: str = diff_text.rstrip("\r\n")
        formatted_diff: FormattedText = to_formatted_text(ANSI(clean_diff))
        total_lines: int = max(1, len(clean_diff.split("\n")))
        scroll_line: int = 0
        error_msg: str = ""

        diff_control = FormattedTextControl(
            text=formatted_diff,
            focusable=False,
            show_cursor=False,
            get_cursor_position=lambda: Point(x=0, y=scroll_line),
        )
        diff_window = Window(
            content=diff_control,
            wrap_lines=True,
            right_margins=[ScrollbarMargin(display_arrows=True)],
        )

        def _scroll_diff(delta: int) -> None:
            nonlocal scroll_line
            info = diff_window.render_info
            current_top = info.vertical_scroll if info is not None else scroll_line
            if delta > 0 and info is not None and info.bottom_visible:
                return
            max_scroll = max(0, total_lines - 1)
            scroll_line = max(0, min(max_scroll, current_top + delta))
            diff_window.vertical_scroll = scroll_line

        def _scroll_pages(direction: int) -> None:
            info = diff_window.render_info
            page_size = max(1, (info.window_height - 2) if info is not None else 20)
            _scroll_diff(direction * page_size)

        def _get_status_bar() -> list[tuple[str, str]]:
            info = diff_window.render_info
            if info is not None:
                top = min(total_lines, info.vertical_scroll + 1)
                bottom = min(total_lines, info.vertical_scroll + info.window_height)
                pos_str = f"Lines {top}-{bottom}/{total_lines}"
            else:
                pos_str = f"Lines 1/{total_lines}"

            if error_msg:
                status = f" [DIFF] {pos_str} | {error_msg} "
            else:
                status = (
                    f" [DIFF] {pos_str} | "
                    "PgUp/PgDn/Alt-J/K: Scroll | "
                    "Alt-j/k: History | Tab: Complete | Ctrl-C/D: Quit "
                )
            return [("reverse", status)]

        status_window = Window(
            content=FormattedTextControl(text=_get_status_bar, focusable=False),
            height=Dimension.exact(1),
            style="reverse",
        )

        def _on_text_changed(_: Buffer) -> None:
            nonlocal error_msg
            if error_msg:
                error_msg = ""

        input_buffer = Buffer(
            completer=completer,
            history=self.history,
            complete_while_typing=False,
            multiline=False,
            on_text_changed=_on_text_changed,
        )

        prompt_window = Window(
            content=BufferControl(
                buffer=input_buffer,
                input_processors=[BeforeInput(prompt)],
            ),
            height=Dimension(min=1, max=5),
            wrap_lines=True,
        )

        root_container = FloatContainer(
            content=HSplit([diff_window, status_window, prompt_window]),
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=8, scroll_offset=1),
                )
            ],
        )

        kb = self._create_key_bindings()

        @kb.add("tab")
        def _tab(event: KeyPressEvent) -> None:
            buf = event.current_buffer
            if buf.complete_state:
                buf.complete_next()
            else:
                buf.start_completion(select_first=False)

        @kb.add("s-tab")
        def _s_tab(event: KeyPressEvent) -> None:
            buf = event.current_buffer
            if buf.complete_state:
                buf.complete_previous()
            else:
                buf.start_completion(select_last=True)

        @kb.add("pageup")
        @kb.add("escape", "v")
        def _page_up(_: KeyPressEvent) -> None:
            _scroll_pages(-1)

        @kb.add("pagedown")
        @kb.add("c-v")
        def _page_down(_: KeyPressEvent) -> None:
            _scroll_pages(1)

        @kb.add("c-up")
        @kb.add("escape", "K")
        def _line_up(_: KeyPressEvent) -> None:
            _scroll_diff(-3)

        @kb.add("c-down")
        @kb.add("escape", "J")
        def _line_down(_: KeyPressEvent) -> None:
            _scroll_diff(3)

        @kb.add("escape", "<")
        def _scroll_top(_: KeyPressEvent) -> None:
            nonlocal scroll_line
            scroll_line = 0
            diff_window.vertical_scroll = 0

        @kb.add("escape", ">")
        def _scroll_bottom(_: KeyPressEvent) -> None:
            nonlocal scroll_line
            scroll_line = max(0, total_lines - 1)
            diff_window.vertical_scroll = scroll_line

        @kb.add("c-c")
        def _interrupt(event: KeyPressEvent) -> None:
            event.app.exit(exception=KeyboardInterrupt)

        @kb.add("c-d")
        def _eof(event: KeyPressEvent) -> None:
            event.app.exit(exception=EOFError)

        @kb.add("enter")
        def _accept(event: KeyPressEvent) -> None:
            nonlocal error_msg
            val = event.current_buffer.text.strip()
            if not val and not default:
                if required:
                    error_msg = "Error: a value is required"
                return
            self.history.append_string(val)
            event.app.exit(result=val)

        app: Application[str] = Application(
            layout=Layout(root_container, focused_element=prompt_window),
            key_bindings=kb,
            full_screen=True,
        )
        return app.run()

    def prompt_input(
        self,
        prompt: str,
        default: str = "",
        required: bool = False,
        complete_with: list[str] | None = None,
        diff_text: str | None = None,
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
        :param diff_text: Optional git diff text to display in a split-pane pager.
        :type diff_text: Optional[str]
        :return: The input string.
        :rtype: str
        """
        all_keywords: set[str] = self.keywords | set(complete_with or [])
        logging.debug("[DEBUG] Keywords: %s", str(all_keywords))
        completer: WordCompleter = WordCompleter(sorted(all_keywords), WORD=True)

        if default:
            prompt += f" (default: {default})"

        save_history: bool = False
        value: str = ""
        try:
            if diff_text and diff_text.strip():
                value = self._prompt_with_diff(
                    prompt=prompt,
                    default=default,
                    required=required,
                    completer=completer,
                    diff_text=diff_text,
                ).strip()
                if value and not value.startswith("/"):
                    save_history = True
            else:
                while True:
                    value = pt_prompt(
                        prompt,
                        history=self.history,
                        completer=completer,
                        complete_while_typing=False,
                        complete_style=CompleteStyle.READLINE_LIKE,
                        key_bindings=self._create_key_bindings(),
                    ).strip()
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
