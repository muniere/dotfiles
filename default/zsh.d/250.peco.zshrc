if (which peco &> /dev/null); then
  #
  # <C-x><C-f>: find file
  #
  function peco-file () {
    local selected
    selected=$(find . -type f -o -type d -maxdepth 10 | grep -v '/\.' | tail -n +2 | peco)
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N peco-file
  bindkey '^x^f' peco-file

  #
  # <C-]>: src with ghq
  #
  function peco-src() {
    local selected
    selected=$(ghq list --full-path | sed -e "s|${HOME}|~|" | peco)
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N peco-src
  bindkey '^]' peco-src

  #
  # <C-[>: git log
  #
  function peco-gitlog () {
    if [[ ! "$BUFFER" =~ "\s*git" ]]; then
      return
    fi

    local selected
    selected=$(git log --oneline | peco | awk '{ print $1 }')
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N peco-gitlog
  bindkey '^[' peco-gitlog

  #
  # <C-@>: branch
  #
  function peco-branch () {
    if [[ ! "$BUFFER" =~ "\s*git" ]]; then
      return
    fi

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
    if which tac &> /dev/null; then
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
