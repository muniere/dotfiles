# ===
# Homebrew
# ===
export HOMEBREW_CASK_OPTS="--appdir=/Applications"

if [ -x /usr/local/bin/brew ]; then
  # HACK: Here needs to remove prefix "/usr/local/bin" and "/usr/local/sbin" from PATH;
  #       `brew shellenv` do nothing if these paths already exists in PATH.`
  export PATH="${PATH#'/usr/local/bin:'}"
  export PATH="${PATH#'/usr/local/sbin:'}"
  eval "$(/usr/local/bin/brew shellenv)"
fi

if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# vim: ft=sh sw=2 ts=2 sts=2
