if (which peco > /dev/null); then
  #
  # <C-o>: find directory
  #
  function peco-dir () {
    local selected
    selected=$(find . -type d -maxdepth 10 | grep -v '/\.' | tail -n +2 | peco)
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N peco-dir
  bindkey '^o'   peco-dir

  #
  # <C-m>: find file
  #
  function peco-file () {
    local selected
    selected=$(find . -type f -maxdepth 10 | grep -v '/\.' | tail -n +2 | peco)
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N peco-file
  bindkey '^j'   peco-file

  #
  # <C-]>: src with ghq
  #
  function peco-src() {
    local selected
    selected="$(ghq list --full-path | peco)"
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N peco-src
  bindkey '^]'   peco-src

  #
  # <C-@>: branch
  #
  function peco-branch () {
    local selected
    selected=$(git branch -vv | peco | awk '$0 = substr($0, 3) { print $1 }')
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N peco-branch
  bindkey '^@' peco-branch

  #
  # <C-r>: history
  #
  function peco-history() {
    local tac
  
    if which tac > /dev/null; then
      tac="tac"
    else
      tac="tail -r"
    fi
  
    local selected
    selected=$(history -n 1 | eval $tac | peco --query "$LBUFFER")
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N peco-history
  bindkey '^r' peco-history
fi
# vim: ft=sh sw=2 ts=2 sts=2
