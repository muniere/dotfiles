# =====
# mise 
# =====
if command -v mise &> /dev/null; then
  if [ -n "$ZSH_VERSION" ]; then
    eval "$(mise activate zsh --shims)"
  elif [ -n "$BASH_VERSION" ]; then
    eval "$(mise activate bash --shims)"
  fi
fi

# =====
# local
# =====
export PATH="$HOME/.local/bin:$PATH"

export PATH=$(distinct $PATH)

# vim: ft=sh sw=2 ts=2 sts=2
