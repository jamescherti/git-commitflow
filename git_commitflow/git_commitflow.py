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
"""Git commitflow command-line interface."""

import argparse
import logging
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Union

from colorama import Fore

from .cache_file import CacheFile
from .helpers import remove_matching_filenames, replace_home_with_tilde
from .readline_manager import ReadlineManager

# TODO: Add configuration file for the following options:
# GIT_DIFF_OPTS = ['--', ':!*.asc', ':!*vault.yaml', ':!*vault.yml']
# MIN_COMMIT_MESSAGE_SIZE = 6
# IGNORE_FILENAMES_REGEX = ["^flycheck_", "^flymake_"]

GIT_DIFF_OPTS: list[str] = []
MIN_COMMIT_MESSAGE_SIZE: int = 1
GIT_COMMITFLOW_DATA_DIR: Path = Path("~/.config/git-commitflow").expanduser()
CACHE_FILE: Path = GIT_COMMITFLOW_DATA_DIR / "repo-data.json"
IGNORE_FILENAMES_REGEX: list[str] = []
HISTORY_LENGTH: int = 256


class GitCommitFlow:
    """
    Main controller for the Git commit workflow.
    """

    def __init__(self) -> None:
        self.args: argparse.Namespace = self._parse_args()
        GIT_COMMITFLOW_DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.git_repo_dir: Path = self._find_git_repo_dir()
        self.branch: str = \
            self._get_first_line_cmd("git symbolic-ref --short HEAD")
        self.amount_commits: int = self._count_commits()
        self.readline_manager: ReadlineManager = \
            self._init_prompt_and_history()
        self.cache: CacheFile = CacheFile(CACHE_FILE)

    def _init_prompt_and_history(self) -> ReadlineManager:
        """
        Initialize history and prompt manager.

        :return: Configured ReadlineManager instance.
        :rtype: ReadlineManager
        """
        # History
        prompt_history_file: Union[Path, None] = None
        dot_git_dir: str = \
            self._get_first_line_cmd("git rev-parse --git-common-dir").strip()
        if not dot_git_dir:
            print("Error: The .git directory could not be located",
                  file=sys.stderr)
            sys.exit(1)

        prompt_history_file = \
            Path(dot_git_dir).joinpath("git-commitflow-history.rl")

        logging.debug("[DEBUG] History file: %s", str(prompt_history_file))

        return ReadlineManager(history_file=prompt_history_file,
                               history_length=HISTORY_LENGTH)

    def _parse_args(self) -> argparse.Namespace:
        """
        Parse command-line arguments.

        :return: Parsed arguments namespace.
        :rtype: argparse.Namespace
        """
        usage: str = "%(prog)s [--option] [args]"
        parser: argparse.ArgumentParser = \
            argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                    usage=usage)
        parser.add_argument(
            "-p",
            "--push",
            default=False,
            action="store_true",
            required=False,
            help=("Git push after a successful commit. (The references are "
                  "pushed only if they have not been pushed previously. The "
                  "git-commitflow tool keeps track of the references that "
                  "have been pushed, preventing the same reference from being "
                  "pushed multiple times. This minimizes redundant pushes.)"),
        )

        # parser.add_argument(
        #     "-r",
        #     "--recursive",
        #     default=False,
        #     action="store_true",
        #     required=False,
        #     help="Apply git-commitflow to all submodules",
        # )

        return parser.parse_args()

    def main(self) -> None:
        """
        Execute the main workflow.
        """
        errno: int = 0

        if self.amount_commits > 0:
            if len(self._run("git --no-pager diff --name-only "
                             "--diff-filter=TXBU HEAD")) > 0:
                print("There is an issue in the repository "
                      f"'{self.git_repo_dir}'.")
                sys.exit(1)

        # Buggy
        # self.git_submodule_foreach()

        if self._run("git status --porcelain"):
            self.git_add()
            errno = self.git_ci()
        else:
            print("[COMMIT] Nothing to commit "
                  f"(Path: '{self.git_repo_dir}').")

        if not errno and self.args.push:
            try:
                self.cache.load()
                self.git_push()
            finally:
                self.cache.save()

        sys.exit(errno)

    # def git_submodule_foreach(self) -> None:
    #     try:
    #         git_commit_wrapper_recursive: int = \
    #             int(os.environ.get("GIT_COMMIT_WRAPPER_RECURSIVE", "0"))
    #     except ValueError:
    #         git_commit_wrapper_recursive = 0
    #
    #     if self.args.recursive or git_commit_wrapper_recursive:
    #         if not (self.git_repo_dir / ".gitmodules").is_file():
    #             return
    #
    #         git_ci_script: Path = Path(__file__).absolute()
    #         print(f"{Fore.LIGHTYELLOW_EX}[SUBMODULE FORREACH] "
    #               f"{self.git_repo_dir}{Fore.RESET}")
    #         cmd: list[str] = ["git", "submodule", "--quiet", "foreach",
    #         "--recursive",
    #                           str(git_ci_script)]
    #         if self.args.push:
    #             cmd += ["--push"]
    #         try:
    #             subprocess.check_call(cmd)
    #         except subprocess.CalledProcessError as proc_err:
    #             print(f"Error: {proc_err}", file=sys.stderr)
    #             sys.exit(1)

    def git_ci(self) -> int:
        """
        Function that performs the git commit.

        :return: Exit status code.
        :rtype: int
        """
        print(f"{Fore.LIGHTYELLOW_EX}[GIT COMMIT] "
              f"{self.git_repo_dir}{Fore.RESET}")
        git_commit_opts: list[str] = ["-a"]

        use_git_commit: bool = False
        try:
            commit_message: str = self.diff_and_get_commit_message()
        except EOFError:
            print()
            while True:
                try:
                    answer = input("Edit the commit message? [y,n] ")
                except KeyboardInterrupt:
                    print()
                    sys.exit(1)

                if answer not in ["y", "n"]:
                    continue

                if answer != "y":
                    sys.exit(1)

                break

            use_git_commit = True

        if use_git_commit:
            cmd: list[str] = ["git", "commit", "-a"]
            print("[RUN] ", subprocess.list2cmdline(cmd))
            subprocess.call(cmd)
        else:
            if commit_message:
                git_commit_opts.extend(["-m", commit_message])
                print(f"Commit message: {commit_message}")
            else:
                git_commit_opts.extend(["--reset-author"])
                if self.amount_commits > 0:
                    # Reuse the commit message of the previous commit
                    git_commit_opts.extend(["--reuse-message=HEAD"])

            print("[RUN] git commit", " ".join(git_commit_opts))
            try:
                subprocess.check_call(["git", "commit"] + git_commit_opts)

                print()
                print(Fore.GREEN + "[COMMIT] git commit was SUCCESSFUL." +
                      Fore.RESET)
            except subprocess.CalledProcessError:
                print()
                print(Fore.RED +
                      "[COMMIT] git commit has FAILED." +
                      Fore.RESET)
                return 1

        return 0

    def git_push(self) -> bool:
        """
        Perform git push sequence.

        :return: Success boolean flag.
        :rtype: bool
        """
        # --------------
        # Load cache
        # --------------
        remote_url: str = self._get_first_line_cmd("git ls-remote  --get-url")

        # ------------------------
        # Init commit refs (cache)
        # ------------------------
        git_push_commit_refs: dict[str, Any] = \
            self.cache.get("git_push_commit_refs", {})

        try:
            git_push_commit_refs[remote_url]
        except KeyError:
            git_push_commit_refs[remote_url] = {}

        try:
            git_push_commit_refs[remote_url][self.branch]
        except KeyError:
            git_push_commit_refs[remote_url][self.branch] = ""

        commit_ref: str = \
            self._get_first_line_cmd("git rev-parse --verify HEAD")

        if commit_ref == git_push_commit_refs[remote_url][self.branch]:
            print(f"[PUSH] Already pushed: {self.git_repo_dir}")
            return True

        # -----------
        # GIT PUSH
        # -----------
        print(f"{Fore.LIGHTYELLOW_EX}[GIT PUSH] "
              f"{self.git_repo_dir}{Fore.RESET}")
        if not self._run(["git", "remote", "-v"]):
            return True  # No git remote

        try:
            # Display the remote branch that is tracked by the current local
            # branch The error message will be: fatal: no such branch: 'master'
            subprocess.check_call(["git", "rev-parse",
                                   "--symbolic-full-name", "HEAD@{u}"],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)

            subprocess.check_call(["git", "fetch", "-a"])
        except subprocess.CalledProcessError as proc_err:
            print(f"Error: {proc_err}", file=sys.stderr)
            return False

        if subprocess.call(["git", "merge", "--ff-only"]) != 0:
            git_pull_cmd: list[str] = [
                "git", "pull", "--rebase", "--autostash"]
            if self.confirm("Git failed to merge fast-forward."
                            "Do you want to run '" +
                            subprocess.list2cmdline(git_pull_cmd) +
                            "'"):
                if subprocess.call(git_pull_cmd) != 0:
                    print("Error with 'git pull --rebase'...")
                    return False

        print()
        print('[RUN] git push')

        success: bool = False
        if subprocess.call(["git", "push"]) == 0:
            print()
            print(f"{Fore.GREEN}[PUSH] git commit and push were "
                  f"SUCCESSFUL.{Fore.RESET}")
            success = True
        else:
            print()
            print(f"{Fore.RED}[PUSH] git commit and push FAILED.{Fore.RESET}")

        # ------------------
        # Update cache file
        # ------------------
        if success:
            commit_ref = \
                self._get_first_line_cmd("git rev-parse --verify HEAD")
            git_push_commit_refs[remote_url][self.branch] = commit_ref
            self.cache.set("git_push_commit_refs", git_push_commit_refs)

        return success

    def git_config_get(self, git_var: str, default_value: str = "") -> str:
        """
        Retrieve Git configuration variable.

        :param git_var: The configuration key to read.
        :type git_var: str
        :param default_value: Default to return on error.
        :type default_value: str
        :return: The Git config value.
        :rtype: str
        """
        try:
            return self._get_first_line_cmd(["git", "config", git_var])
        except subprocess.CalledProcessError:
            return default_value

    def _find_git_repo_dir(self) -> Path:
        """
        Locate top-level Git repository directory.

        :return: Path to repository directory.
        :rtype: Path
        """
        try:
            repo_dir: Path = Path(
                self._get_first_line_cmd("git rev-parse --show-toplevel",
                                         check=True)
            )
            if not repo_dir.is_dir():
                print(f"Error: The Git repository '{repo_dir}' "
                      "is not a directory", file=sys.stderr)
                sys.exit(1)
            return repo_dir
        except subprocess.CalledProcessError as proc_err:
            print(f"Error: {proc_err}", file=sys.stderr)
            sys.exit(1)

    def _count_commits(self) -> int:
        """
        Count commits in current branch.

        :return: Commit count.
        :rtype: int
        """
        output: str = \
            self._get_first_line_cmd("git rev-list --all --count")
        return int(output) if output.isdigit() else 0

    def _get_first_line_cmd(
            self, cmd: Union[str, list[str]], **kwargs: Any) -> str:
        """
        Execute command and fetch first output line.

        :param cmd: Command to run.
        :type cmd: Union[str, list[str]]
        :param kwargs: Additional arguments for subprocess.
        :type kwargs: Any
        :return: First line of output.
        :rtype: str
        """
        output: list[str] = self._run(cmd, **kwargs)
        try:
            return output[0]
        except IndexError:
            return ""

    def _run(self, command: Union[str, list[str]],
             check: bool = False, text: bool = True) -> list[str]:
        """
        Execute command.

        :param command: Command to run.
        :type command: Union[str, list[str]]
        :param check: Check return code flag.
        :type check: bool
        :param text: Text mode flag.
        :type text: bool
        :return: Output lines.
        :rtype: list[str]
        """
        if isinstance(command, str):
            command_list: list[str] = shlex.split(command)
        else:
            command_list = command
        result: subprocess.CompletedProcess = subprocess.run(
            command_list, stdout=subprocess.PIPE,
            check=check, text=text
        )
        if text:
            return str(result.stdout).splitlines()
        return []

    def git_add(self) -> None:
        """
        Interactive file addition to Git index.
        """
        list_untracked_files: list[str] = self._run(
            ["git", "-C", str(self.git_repo_dir),
             "ls-files", "--others",
             "--exclude-standard"]
        )
        list_untracked_files = remove_matching_filenames(
            list_untracked_files,
            IGNORE_FILENAMES_REGEX,
        )
        untracked_paths: list[str] = [str(self.git_repo_dir / item)
                                      for item in list_untracked_files]
        if untracked_paths:
            print("Git repository:", self.git_repo_dir)
            print()
            print("Files:")
            for untracked_file in untracked_paths:
                print(" ", replace_home_with_tilde(Path(untracked_file)))

            print()
            while True:
                answer: str = input("git add? [y,n] ")
                if answer.lower() == "y":
                    self._run(["git", "add"] + untracked_paths)
                    break

                if answer.lower() == "n":
                    break

    def diff_and_get_commit_message(self) -> str:
        """
        Display diff and prompt user for a commit message.

        :return: Commit message.
        :rtype: str
        """
        if self.amount_commits > 0:
            # Diff against HEAD shows both staged and unstaged changes
            cmd: list[str] = (["git", "--paginate", "diff",
                              "--diff-filter=d", "--color"] + ["HEAD"]
                              + GIT_DIFF_OPTS)
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                # Ignore errors
                pass

        git_name: str = self.git_config_get("user.name", "Unknown")
        # git_email: str = self.git_config_get(
        #     "user.email", "unknown@domain.ext")
        # git_author = f"{git_name} <{git_email}>"
        git_author: str = f"{git_name}"

        # commit_message = self.git_config_get("custom.commit-message").strip()
        # previous_message = ""
        # if commit_message:
        #     print(Fore.YELLOW + commit_message + Fore.RESET)

        prompt: str = "Commit message: "
        if self.amount_commits > 0:
            # previous_message = \
            #     "\n".join(
            #         self._run("git --no-pager log -1 --pretty=%B")).rstrip()
            # prompt = (
            #     Fore.YELLOW + self.git_repo_dir.name +
            #     Fore.RESET + " " +
            #     f"({Fore.YELLOW + self.branch + Fore.RESET}): "
            #     f"{Fore.YELLOW + git_author + Fore.RESET}> ")
            prompt = (self.git_repo_dir.name +
                      f" ({self.branch}): {git_author}> ")
            # print(Fore.YELLOW + previous_message + Fore.RESET)
            # self.readline_manager.append_to_history(previous_message)

        # commit_message = self.prompt_git_commit_message(prompt,
        #                                                 commit_message)
        commit_message: str = self.prompt_git_commit_message(prompt, "")

        # TODO: add a confirmation?
        # subprocess.check_call(["git", "status"])

        # TODO: move this to a function
        # logging.debug("[DEBUG] Previous message: %s", previous_message)
        logging.debug("[DEBUG] Commit message: %s", commit_message)

        return commit_message

    def prompt_git_commit_message(self, prompt: str,
                                  commit_message: str) -> str:
        """
        Interactive loop prompting for a commit message.

        :param prompt: Command line prompt string.
        :type prompt: str
        :param commit_message: Initial default value.
        :type commit_message: str
        :return: Final commit message.
        :rtype: str
        """
        while True:
            try:
                commit_message = \
                    self.readline_manager.readline_input(prompt=prompt)
            except KeyboardInterrupt:
                sys.exit(0)

            if commit_message == "":
                continue

            if len(commit_message) > 0 and \
               len(commit_message) < MIN_COMMIT_MESSAGE_SIZE:
                print("Error: the commit message is too short.")
                print()
            else:
                break

        return commit_message

    @staticmethod
    def confirm(prompt: str) -> bool:
        """
        Ask a yes or no question.

        :param prompt: The prompt to present to the user.
        :type prompt: str
        :return: A boolean corresponding to yes or no.
        :rtype: bool
        """
        while True:
            try:
                answer: str = input(f"{prompt} [y,n] ")
            except KeyboardInterrupt:
                print()
                sys.exit(1)

            if answer not in ["y", "n"]:
                continue

            return bool(answer == "y")
