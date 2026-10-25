# git-commitflow - Never make mistakes when committing using Git
![License](https://img.shields.io/github/license/jamescherti/git-commitflow)

- Author: James Cherti <[https://www.jamescherti.com/](https://www.jamescherti.com/)>
- License: GPL

The **[git-commitflow](https://github.com/jamescherti/git-commitflow)** tool is an interactive command-line interface that combines `git add`, `git diff`, `git commit`, and `git push` into a single, mistake-proof workflow.

One of the main benefits of `git-commitflow` is that it gives you full visibility into your changes before they are committed.

Every developer has experienced the consequences of running Git commands from muscle memory at the end of a long coding session.

For example, you finally fix a bug, run `git add .` and `git commit -a -m "Commit message."` without inspecting the full diff, and push to the remote repository, only to realize moments later that your commit included leftover debug statements, temporary configuration edits, or untracked files. Even when the changes are clean, discovering after committing that the remote branch has diverged forces you to stop, manually stash, and rebase an unnecessary merge commit.

## The workflow

Running **git-commitflow** guides you through the following steps in order:

- Prompting to add files (`git add`).
- Displaying `git diff` to verify accuracy and prevent mistakes before committing.
- Prompting to enter a commit message. (The interactive prompt supports `Tab` autocompletion for commands such as `/reset` to cancel the diff and hard reset the repository, `/edit` to open the Git editor, and `/skip` to exit the program without making any changes.)
- It commits the changes (`git commit`).
- Optional (`-p` / `--push` flag): Synchronizes changes and pushes updates to the remote repository (`git push`). Before pushing, it fetches remote changes and attempts a fast-forward merge (`--ff-only`); if the merge fails, it prompts the user to confirm whether to proceed with a rebase (`--rebase` and `--autostash`). The references are only pushed when they have never been pushed before.

### Interactive prompt features

When prompted for a commit message, the interactive prompt (powered by `prompt_toolkit`) supports:

- Use the standard arrow keys (`Up`, `Down`, `Left`, `Right`) or Vim-style `Alt+k` (up), `Alt+j` (down), `Alt+h` (left), and `Alt+l` (right) to move the cursor and cycle through previous commit messages stored in the repository's history.
- Jump by word backward using `Alt+Shift+Left` and forward using `Alt+Shift+Right`.
- Press `Tab` to autocomplete built-in slash commands (`/reset`, `/edit`, `/skip`) without distracting pop-up menus appearing while you type.
- Entering `/edit` opens the default Git editor, similar to the behavior when executing `git commit -a`.

## Requirements

- git >= 2.6
- Python, pip, and [prompt_toolkit](https://pypi.org/project/prompt-toolkit/) (installed automatically with `pip`)

## Installation

Here is how to install `git-commitflow` using [pip](https://pypi.org/project/pip/):
```bash
pip install --user git-commitflow
```

The pip command above will install the `git-commitflow` executable in `~/.local/bin/git-commitflow`.

### Optional Python Dependencies

The `git-commitflow` CLI supports optional dependencies that extend its functionality. These extras can be installed based on environment requirements.

#### Colored Terminal Output

The following installs `colorama` to provide consistent cross-platform ANSI color support. This enhances the readability of standard output and error messages.

```bash
pip install --user "git-commitflow[colors]"
```

#### Custom Process Title

The following installs `setproctitle` to rename the running process from `python` to `git-commitflow`. This simplifies identification and management in system monitoring tools such as `top`, `htop`, and `ps`.

```bash
pip install --user "git-commitflow[proctitle]"
```

#### Install both

To install both extras at once, use a comma-separated list:

```bash
pip install --user "git-commitflow[colors,proctitle]"
```

## Usage

### Example usage

To use the tool within your Git repository, run:

```bash
git commitflow
```

This command will guide you through the following steps interactively:

* **Stage untracked files**: Prompts you to `git add` any untracked files that haven't been staged.
* **Review changes**: Displays a diff of your changes, allowing you to confirm whether you want to proceed with the commit.
* **Commit changes**: Enter a commit message (using arrow keys or `Alt+h`/`j`/`k`/`l` to navigate history and text, `Alt+Shift+Left`/`Alt+Shift+Right` to jump words, or `Tab` to complete `/reset`, `/edit`, and `/skip`) to finalize the commit.

If you also wish to synchronize and push the changes, you can use the `--push` option:

```bash
git commitflow --push
```

The references are pushed only if they have not been pushed previously. The `git-commitflow` tool keeps track of the references that have been pushed, preventing the same reference from being pushed multiple times. This minimizes redundant pushes.

### Command-line arguments

```text
usage: git-commitflow [--option] [args]

Git commitflow command-line interface.

positional arguments:
  files       Files to commit. If none are specified, commits all files.

options:
  -h, --help  show this help message and exit
  -p, --push  Git push after a successful commit.
```

## Customizations

### Git configuration alias

To enhance your workflow, add the following aliases to your `~/.gitconfig` file:

```ini
[alias]
ci = commitflow
cip = commitflow --push
```

With these aliases, you can use the commands `git ci` to commit changes and `git cip` to commit and push in a single step.

## License

Copyright (c) 2020-2026 [James Cherti](https://www.jamescherti.com)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Links

- [git-commitflow @GitHub](https://github.com/jamescherti/git-commitflow)

- [git-commitflow @PyPI](https://pypi.org/project/git-commitflow/)
