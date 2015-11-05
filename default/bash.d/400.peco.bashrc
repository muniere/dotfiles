if (which peco > /dev/null); then
  # src with ghq
  peco-src() {
    local selected
    selected="$(ghq list --full-path | peco --query="$READLINE_LINE")"
    if [ -n "$selected" ]; then
      READLINE_LINE="cd $selected"
      READLINE_POINT=${#READLINE_LINE}
    fi
    }
  bind -x '"\C-]": peco-src'
fi

# vim: ft=sh sw=2 ts=2 sts=2
