#!/usr/bin/env bash

# ===
# Variables
# ===
GHQ_ROOT_DEFAULT="${HOME}/Projects/src"
GHQ_ROOT_CONFIG="$(git config --get ghq.root)"
GHQ_ROOT="${GHQ_ROOT:-"${GHQ_ROOT_CONFIG}"}"
GHQ_ROOT="${GHQ_ROOT:-"${GHQ_ROOT_DEFAULT}"}"
GHQ_ROOT="${GHQ_ROOT/#\~/$HOME}"
DOTFILES_DIR="${GHQ_ROOT}/github.com/muniere/dotfiles"
DOTFILES_URL="https://github.com/muniere/dotfiles.git"

# ===
# Functions
# ===
function clone-repo() {
if ! [ -d "${DOTFILES_DIR}" ]; then
    git clone "${DOTFILES_URL}" "${DOTFILES_DIR}"
fi
}

function bundle-core() {
case "$OSTYPE" in
    darwin*)
        # https://brew.sh
        if ! (which brew &> /dev/null); then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

            # for intel chip
            if [ -x /usr/local/bin/brew ]; then
                eval "$(/usr/local/bin/brew shellenv)"
            fi

            # for apple chip
            if [ -x /opt/homebrew/bin/brew ]; then
                eval "$(/opt/homebrew/bin/brew shellenv)"
            fi
        fi

        # https://github.com/Homebrew/homebrew-bundle
        brew bundle install --no-lock --file vault/brew/core/Brewfile
        ;;

    *) ;;
esac
}

function bundle-more() {
case "$OSTYPE" in
    darwin*)
        # https://github.com/Homebrew/homebrew-bundle
        brew bundle install --no-lock --file vault/brew/more/Brewfile
        ;;

    *) ;;
esac
}

function link-files() {
cd "${DOTFILES_DIR}" 
deno task link
cd -
}

# ===
# Main
# ===
set -eux

clone-repo

bundle-core

link-files

bundle-more
