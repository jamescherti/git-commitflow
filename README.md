# git-commitflow - A Git Add, Diff, Commit, and Push Helper
![License](https://img.shields.io/github/license/jamescherti/outline-indent.el)

## Introduction

The `git-commitflow` tool is an interactive command-line interface that assists with the Git operations.

Running `git-commitflow` guides the user through the following interactive steps:
- Prompting the user to add files (`git add`).
- Displaying differences to ensure accuracy and prevent mistakes before committing (`git diff`).
- Prompting the user to enter a commit message and then committing the changes (`git commit`).
- It first attempts to merge using `--ff-only`; if the merge fails, it prompts the user to confirm whether to proceed with a rebase using `--rebase` and `--autostash`. Afterward, it commits the changes.
- Optional (`-p` flag): Pushing updates to the remote repository (`git push`). The references are only pushed when they have never been pushed before. The `git-commitflow` tool maintains a list of references that have been pushed, preventing multiple pushes of the same reference. This reduces unnecessary pushes.

One significant benefit of the `git-commitflow` tool is that it enhances the user's awareness and control over their changes before committing. This reduces the likelihood of including unintended files or alterations in commits, promoting a cleaner and more organized version history.

When prompted for a commit message, the user can press the up arrow to quickly access previous messages, utilizing the readline prompt history. Additionally, pressing Ctrl-d will open the Git editor, similar to the behavior when executing `git commit -a`.

Additionally, the tool simplifies the workflow for adding, committing, and pushing changes, making the overall Git experience more efficient and user-friendly.

## Requirements

- git >= 2.6
- Python and pip

## Installation

Here is how to install `git-commitflow` using [pip](https://pypi.org/project/pip/):
```
pip install --user git-commitflow
```

The pip command above will install the `git-commitflow` executable in the directory `~/.local/bin/`.

## Usage

### Example usage

To use the tool within your Git repository, run:

```bash
git commitflow
```

This command will guide you through the following steps interactively:

- **Stage untracked files**: Prompts you to `git add` any untracked files that haven't been staged.
- **Review changes**: Displays a diff of your changes, allowing you to confirm whether you want to proceed with the commit.
- **Commit changes**: Once you validate your commit message, the tool will finalize the commit.

If you also wish to push the changes, you can use the `--push` option:

```bash
git commitflow --push
```

(The references are pushed only if they have not been pushed previously. The `git-commitflow` tool keeps track of the references that have been pushed, preventing the same reference from being pushed multiple times. This minimizes redundant pushes.)

This will git add, diff, commit, push your changes to the remote repository after the commit.

### Command-line arguments

```
usage: git-commitflow [--option] [args]

Readline manager.

options:
  -h, --help       show this help message and exit
  -p, --push       Git push after a successful commit
  -r, --recursive  Apply git-commitflow to all submodules
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

Copyright (c) 2020-2025 [James Cherti](https://www.jamescherti.com)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Links

- [git-commitflow @GitHub](https://github.com/jamescherti/git-commitflow)
- [git-commitflow @PyPI](https://pypi.org/project/git-commitflow/)
