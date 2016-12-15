if (which fzf &> /dev/null); then
  #
  # <C-x><C-f>: find file
  #
  function fzf-file () {
    local selected
    selected=$(find . -maxdepth 10 | grep -v '/\.' | tail -n +2 | fzf)
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N fzf-file
  bindkey '^x^f' fzf-file

  #
  # <C-]>: src with ghq
  #
  function fzf-src() {
    local selected
    selected=$(ghq list --full-path | sed -e "s|${HOME}|~|" | fzf)
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N fzf-src
  bindkey '^]' fzf-src

  #
  # <C-@>: git log
  #
  function fzf-gitlog () {
    if [[ ! "$BUFFER" =~ "\s*git" ]]; then
      return
    fi

    local selected
    selected=$(git log --oneline | fzf | awk '{ print $1 }')
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N fzf-gitlog
  bindkey '^@' fzf-gitlog

  #
  # <C-[>: branch
  #
  function fzf-branch () {
    if [[ ! "$BUFFER" =~ "\s*git" ]]; then
      return
    fi

    local selected
    selected=$(git branch -vv | fzf | awk '$0 = substr($0, 3) { print $1 }')
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N fzf-branch
  bindkey '^[' fzf-branch

  #
  # <C-r>: history
  #
  function fzf-history() {
    local tac
    if which tac &> /dev/null; then
      tac="tac"
    else
      tac="tail -r"
    fi
  
    local selected
    selected=$(history 1 | eval $tac | fzf  --query "$LBUFFER" | awk '{$1=""; print $0}' | xargs)
    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }
  zle -N fzf-history
  bindkey '^r' fzf-history

  export FZF_DEFAULT_OPTS='--reverse --bind ctrl-k:kill-line --bind ctrl-j:execute::'
fi
# vim: ft=sh sw=2 ts=2 sts=2

