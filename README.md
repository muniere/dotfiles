# dotfiles

## Prerequisites

- [Deno](https://deno.land/) runtime

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
$ deno task setup

# Create symlinks
$ deno task link
```

## Tasks

Each task has following options:

- `-n`: dry-run
- `-v`: verbose

```bash
# Show current link status
deno task status

# Initial setup
deno task setup

# Create symlinks
deno task link

# Remove symlinks
deno task unlink

# Recreate symlinks
deno task relink

# Clean up broken links
deno task cleanup
```

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

## Structure

```
.
├── app/                  # CLI application entry point
├── lib/                  # Shared library modules
└── vault/                # Configuration files for various tools
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
