# git-commitflow - A git add/diff/commit/push helper

The `git-submit` command-line tool enhances the process of staging (`git add`), diff (`git diff`), committing (`git commit`), and pushing (`git push`) in a Git repository.

## Installation

Here is how to install `git-commitflow` using [pip](https://pypi.org/project/pip/):
```
sudo pip install git+https://github.com/jamescherti/git-commitflow
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

## License

Copyright (c) 2020-2024 [James Cherti](https://www.jamescherti.com)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Links

- [git-commitflow @GitHub](https://github.com/jamescherti/git-commitflow)
