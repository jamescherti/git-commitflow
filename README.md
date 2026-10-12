# git-commitflow - Never make mistakes when committing using Git
![License](https://img.shields.io/github/license/jamescherti/git-commitflow)

## Introduction

The **[git-commitflow](https://github.com/jamescherti/git-commitflow)** tool is an interactive command-line interface that combines `git add`, `git diff`, branch synchronization, `git commit`, and `git push` into a single, mistake-proof workflow.

A key benefit of **git-commitflow** is that it gives you complete visibility your changes before they are committed. Enforcing an interactive diff review before every commit catches unintended edits, leftover debug code, and stray files early, keeping your Git history clean.

Running `git-commitflow` guides you through the following steps in order:

- Prompting to add files (`git add`).
- Displaying `git diff` to verify accuracy and prevent mistakes before committing.
- Prompting to enter a commit message. (The prompt supports commands such as `/reset` to cancel the diff and hard reset the repository, `/edit` to open the Git editor, and `/skip` to exit the program without making any changes.)
- Synchronizing changes before finalizing the commit: it first attempts a fast-forward merge (`--ff-only`). If the merge fails, it prompts the user to confirm whether to proceed with a rebase (`--rebase` and `--autostash`). Afterward, it commits the changes (`git commit`).

Optional (`-p` flag) makes **git-commitflow** pushe updates to the remote repository (`git push`). The references are only pushed when they have never been pushed before. The `git-commitflow` tool maintains a list of references that have been pushed, preventing multiple pushes of the same reference and reducing unnecessary network calls.

When prompted for a commit message, the user can press the up arrow to quickly access previous messages via the readline prompt history. Entering `/edit` opens the default Git editor, similar to the behavior when executing `git commit -a`.

## Requirements

- git >= 2.6
- Python and pip

## Installation

Here is how to install `git-commitflow` using [pip](https://pypi.org/project/pip/):
```bash
pip install --user git-commitflow
```

The pip command above will install the `git-commitflow` executable in the directory `~/.local/bin/`.

### Optional Python Dependencies

The `git-commitflow` CLI supports optional dependencies that extend its functionality. These extras can be installed based on environment requirements.

**Colored Terminal Output (`colors`)**: Installs `colorama` to provide consistent cross-platform ANSI color support. This enhances the readability of standard output and error messages.

```bash
pip install --user "git-commitflow[colors]"
```

**Custom Process Title (`proctitle`)**: Installs `setproctitle` to rename the running process from `python` to `git-commitflow`. This simplifies identification and management in system monitoring tools such as `top`, `htop`, and `ps`.

```bash
pip install --user "git-commitflow[proctitle]"
```

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

- **Stage untracked files**: Prompts you to `git add` any untracked files that haven't been staged.
- **Review changes**: Displays a diff of your changes, allowing you to confirm whether you want to proceed with the commit.
- **Commit changes**: Once you validate your commit message, the tool synchronizes the branch and finalizes the commit.

If you also wish to push the changes, you can use the `--push` option:

```bash
git commitflow --push
```

(The references are pushed only if they have not been pushed previously. The `git-commitflow` tool keeps track of the references that have been pushed, preventing the same reference from being pushed multiple times. This minimizes redundant pushes.)

This will git add, diff, commit, push your changes to the remote repository after the commit.

### Command-line arguments

```text
usage: git-commitflow [--option] [args]

options:
  -h, --help       show this help message and exit
  -p, --push       Git push after a successful commit
```

## Customizations

### Git configuration alias

To enhance your workflow, add the following aliases to your `~/.gitconfig` file:

```ini
[alias]
ci = commitflow
cip = commitflow --push
```

With these aliases, you can conveniently use the commands `git ci` to commit changes and `git cip` to commit and push in a single step.

## License

Copyright (c) 2020-2026 [James Cherti](https://www.jamescherti.com)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Links

- [git-commitflow @GitHub](https://github.com/jamescherti/git-commitflow)
- [git-commitflow @PyPI](https://pypi.org/project/git-commitflow/)
