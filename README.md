# dotfiles

## Prerequisites

- [Go](https://go.dev/) toolchain
- `make`

## Installation

### Quick Install

```bash
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/muniere/dotfiles/master/install.sh)"
```

### Manual Install

```bash
# Clone the repository
$ git clone https://github.com/muniere/dotfiles.git
$ cd dotfiles

# Initial setup
$ make setup

# Create symlinks
$ make link
```

## Tasks

The tasks run with `go run`, so there is no need to build beforehand.
The dependencies get fetched on the first run.

```bash
# Show current link status
make status

# Initial setup
make setup

# Create symlinks
make link

# Remove symlinks
make unlink

# Recreate symlinks
make relink

# Clean up broken links
make cleanup
```

Each task has following options, which are passed with `ARGS`:

- `-n`: dry-run
- `-v`: verbose

```bash
make link ARGS="-n -v"

# Or without make
go run . link -n -v
```

`make` also provides the tasks for development: `test` and `fmt`.

## Vaults

### Configuration Files

The `vault/` directory contains files for each tool.

- configuration files
- activation scripts
- executable files

### Platform Support

Configurations are organized by platform.

```
vault/<tool>/
├── default/   # Platform-independent configurations
├── darwin/    # macOS-specific configurations
├── linux/     # Linux-specific configurations
└── template/  # Template files
```

### Templates

A template gets rendered into a file such as `~/.bashrc`, which other tools may write as well.
So the rendered text is kept as a section of the file, enclosed by the marker lines below,
and the lines outside of it are left as they are. Unlinking removes only the section.

```bash
# >>> muniere/dotfiles >>>
...
# <<< muniere/dotfiles <<<
```

## Structure

```
.
├── main.go               # CLI application entry point
├── Makefile              # Tasks to run the commands, and to develop
├── internal/             # Packages of the CLI
│   ├── action/           # Commands: status, setup, link, unlink, cleanup
│   ├── chef/             # Types to define how a tool gets installed
│   └── ...               # Supporting packages: fspath, shell, logging, plist, idea, ...
└── vault/                # Configuration files for various tools, each with its cook book
    ├── mod.go            # List of the cook books
    ├── AndroidStudio/    # Android Studio configurations
    ├── asdf/             # asdf version manager
    ├── bash/             # Bash shell
    ├── bat/              # bat (cat alternative)
    ├── brew/             # Homebrew package lists
    ├── claude/           # Claude Code
    ├── Code/             # Visual Studio Code
    ├── desktop/          # Desktop environment
    ├── docker/           # Docker
    ├── gh/               # GitHub CLI
    ├── ghostty/          # Ghostty terminal emulator
    ├── git/              # Git
    ├── gradle/           # Gradle
    ├── IntelliJIdea/     # IntelliJ IDEA configurations
    ├── iterm/            # iTerm2
    ├── launchd/          # macOS launchd services
    ├── mise/             # mise version manager
    ├── node/             # Node.js
    ├── nvim/             # Neovim
    ├── python/           # Python
    ├── rio/              # Rio terminal emulator
    ├── sh/               # POSIX shell
    ├── sqlfluff/         # SQL linter
    ├── terminal-palette/ # Terminal color palettes
    ├── tig/              # tig (Git TUI)
    ├── tmux/             # Tmux
    ├── vi/               # Vi editor
    ├── vim/              # Vim
    ├── Xcode/            # Xcode
    ├── yazi/             # Yazi file manager
    ├── zsh/              # Zsh shell
    └── zsh-prompt/       # Zsh prompt themes
```
