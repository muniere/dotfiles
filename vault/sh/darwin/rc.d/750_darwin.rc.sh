# =====
# Shell
# =====

# Locale
unset LC_ALL

# ls
alias ls="ls -Gv"

if command -v eza &> /dev/null; then
  alias ll="eza -lF --icons --time-style=long-iso"
  alias l="eza -lAF --icons --time-style=long-iso"
else
  alias ll="ls -lhF"
  alias l="ls -lAhF"
fi

# grep
alias grep="grep --color=always"
alias egrep="egrep --color=always"

# ===
# Java
# ===
if command -v java &> /dev/null; then
  export JAVA_HOME=$(/usr/libexec/java_home)
  export JAVA_OPTS="-Dfile.encoding=UTF-8"
fi

# =====
# Android
# =====
if [ -d $HOME/Library/Android/sdk ]; then
  export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"
  export PATH="$HOME/Library/Android/sdk/tools/bin:$PATH"
  export PATH="$HOME/Library/Android/sdk/emulator:$PATH"
fi

# =====
# CocoaPods
# =====
if [ -n "$XDG_CACHE_HOME" ]; then
  export CP_HOME_DIR="$XDG_CACHE_HOME/cocoapods"
fi

# =====
# Git
# =====
if [ -d $HOMEBREW_PREFIX/share/git-core/contrib/diff-highlight/ ]; then
  export PATH="$HOMEBREW_PREFIX/share/git-core/contrib/diff-highlight:$PATH"
fi

# =====
# Mint
# =====
if [ -n "$XDG_CACHE_HOME" ]; then
  export MINT_PATH="$XDG_CACHE_HOME/mint"
  export MINT_LINK_PATH="$MINT_PATH/bin"
fi

# =====
# MySQL
# =====
if ! command -v mysql &> /dev/null && [ -d $HOMEBREW_PREFIX/opt/mysql ]; then
  export PATH="$HOMEBREW_PREFIX/opt/mysql/bin:$PATH"
fi

if ! command -v mysql &> /dev/null && [ -d $HOMEBREW_PREFIX/opt/mysql@5.7 ]; then
  export PATH="$HOMEBREW_PREFIX/opt/mysql@5.7/bin:$PATH"
fi

if ! command -v mysql &> /dev/null && [ -d $HOMEBREW_PREFIX/opt/mysql-client ]; then
  export PATH="$HOMEBREW_PREFIX/opt/mysql-client/bin:$PATH"
fi

# =====
# pkgconfig
# =====
if [ -d $HOMEBREW_PREFIX/opt/pkg-config ]; then
  export PKG_CONFIG_PATH="/opt/X11/lib/pkgconfig"
fi

# =====
# Python
# =====
if ! command -v python &> /dev/null &&  [ -d $HOMEBREW_PREFIX/opt/python ]; then
  export PATH="$HOMEBREW_PREFIX/opt/python/libexec/bin:$PATH"
fi

if [ -f $HOMEBREW_PREFIX/bin/virtualenvwrapper.sh ]; then
    export WORKON_HOME=$HOME/.virtualenvs
    source $HOMEBREW_PREFIX/bin/virtualenvwrapper.sh
fi

# =====
# Ruby
# =====
if [ -d $HOMEBREW_PREFIX/opt/ruby/bin ]; then
  export PATH="$HOMEBREW_PREFIX/opt/ruby/bin:$PATH"
fi

# =====
# mise / asdf
# =====
if command -v mise &> /dev/null; then
  if [ -n "$ZSH_VERSION" ]; then
    eval "$(mise activate zsh)"
  elif [ -n "$BASH_VERSION" ]; then
    eval "$(mise activate bash)"
  fi
elif [ -f $HOMEBREW_PREFIX/opt/asdf/libexec/asdf.sh ]; then
  source $HOMEBREW_PREFIX/opt/asdf/libexec/asdf.sh
fi

# =====
# Claude Code
# =====
if [ -d $HOME/.claude/local ]; then
  export PATH="$HOME/.claude/local:$PATH"
fi

# vim: ft=sh sw=2 ts=2 sts=2
