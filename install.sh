#!/usr/bin/env bash

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
        brew bundle install --no-lock --file pref/darwin/homebrew/core/Brewfile
        ;;

    *) ;;
esac
}

function bundle-more() {
case "$OSTYPE" in
    darwin*)
        # https://github.com/Homebrew/homebrew-bundle
        brew bundle install --no-lock --file pref/darwin/homebrew/more/Brewfile
        ;;

    *) ;;
esac
}

# main
set -euxv

bundle-core

deno task link

bundle-more
