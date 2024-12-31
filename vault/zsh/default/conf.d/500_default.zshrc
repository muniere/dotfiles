# =====
# Zsh : Hooks
# =====
function zshaddhistory() { 
  emulate -L zsh

  if (! whence ${${(z)1}[1]} >| /dev/null); then
    return 1
  fi

  if [[ ${1%%$'\n'} =~ ${~HISTORY_IGNORE} ]]; then
    # hit: return 1; DO NOT push to history
    return 1
  else 
    # miss: return 0; DO push to history 
    return 0
  fi
} 

function precmd() {
  # update terminal title
  if (echo $TERM | grep -i "xterm" 2>&1 >/dev/null); then
    title="${PWD/$HOME/~}"
    echo -ne "\033]0;${title}\007"
  fi

  # update vcs info
  psvar=()
  LANG=C vcs_info
  psvar[1]="$vcs_info_msg_0_"
}

# =====
# Zsh : Overrides
# =====

# sudo.vim
function sudo() { 
  local args
  case $1 in
    vi|vim)
      args=()
      for arg in $@[2,-1]; do
        if [ $arg[1] = '-' ]; then
          args[$(( 1+$#args ))]=$arg
        else
          args[$(( 1+$#args ))]="sudo:$arg"
        fi
      done
      command vim $args;;
    *)
      command sudo $@;;
  esac
} 

# =====
# Zsh : Completion
# =====
if [ -d $XDG_DATA_HOME/zsh/site-functions ]; then
  export FPATH="$XDG_DATA_HOME/zsh/site-functions:$FPATH"
fi

autoload -Uz colors; colors
autoload -Uz compinit && compinit -C
setopt auto_cd
setopt auto_menu
setopt autopushd
setopt list_packed
setopt list_types
setopt magic_equal_subst
setopt noautoremoveslash
setopt nonomatch
setopt print_eight_bit
setopt pushd_ignore_dups
zstyle ':completion:*' verbose yes
zstyle ':completion:*' completer _expand _complete _match
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'
zstyle ':completion:*' group-name ''
zstyle ':completion:*:default' menu select=1
zstyle ':completion:*:sudo:*' command-path /usr/local/sbin /usr/local/bin /usr/sbin /usr/bin /sbin /bin
zstyle ':completion:*:options' description 'yes'
zstyle ':completion:*:messages' format '%F{yellow}%d%f'$DEFAULT
zstyle ':completion:*:warnings' format '%F{red}No matches for:%F{yellow}%d'$DEFAULT
zstyle ':completion:*:descriptions' format '%F{cyan}%B%d%b%f'$DEFAULT

# =====
# Zsh : Prompt
# =====
function prefix() {
  # print nothing
}

function suffix() {
  if [[ -n "$VIRTUAL_ENV" && -n "$DIRENV_DIR" ]]; then
    echo " ($(basename $VIRTUAL_ENV))"
  fi
}

autoload -Uz vcs_info
setopt prompt_subst
setopt transient_rprompt
zstyle ':vcs_info:*' formats '[%b]'
zstyle ':vcs_info:*' actionformats '[%b|%a]'
PROMPT='$(prefix)%(?.%F{cyan}.%F{red})%n%f@%(?.%F{cyan}.%F{red})%m%f$(suffix): %F{yellow}%~%f
%(!.#.%%) '
RPROMPT='%1(v|%F{magenta}%1v%f|)'

# =====
# Zsh : History
# =====
HISTORY_IGNORE='^(l$|l |ls|la|ll|cd|rm|man|git|tig|gh|which|type)|^[0-9A-Za-z_-]+$'
HISTSIZE=100000
SAVEHIST=100000
setopt hist_ignore_all_dups
setopt hist_ignore_dups
setopt hist_ignore_space
setopt hist_find_no_dups
setopt hist_save_no_dups
setopt hist_reduce_blanks
setopt extended_history
setopt combining_chars
setopt share_history

# =====
# Zsh : Keys
# =====
bindkey -d
bindkey -e

for x in {!..~}; do 
  bindkey -r "^[${x}"
  bindkey -r "^[^${x}"
  bindkey -r "^[[${x}"
  bindkey -r "^[O${x}"
  bindkey -r "^X${x}"
  bindkey -r "^X^${x}"
done

autoload history-search-end
zle -N history-beginning-search-backward-end history-search-end
zle -N history-beginning-search-forward-end history-search-end
bindkey "^P" history-beginning-search-backward-end
bindkey "^N" history-beginning-search-forward-end 
bindkey -r "^S"
bindkey -r "^G"

# =====
# Zsh : Time
# =====
TIMEFMT=$'\nreal\t%E\nuser\t%U\nsys\t%S'

# =====
# direnv : Completion
# =====
if (which direnv &> /dev/null); then
  eval "$(direnv hook zsh)"
fi

# =====
# fzf : Binding
# =====

if (which fzf &> /dev/null); then
  # <C-x><C-f>: find file
  function fzf-file () {
    local selected
    if (which fd &> /dev/null); then
      selected=$(fd --max-depth 20 --type f --hidden --exclude .git | fzf)
    else
      selected=$(find . -maxdepth 20 -type f -not -path '*/\.git/*' | fzf)
    fi

    if [ -n "$selected" ]; then
      BUFFER="${BUFFER}${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }

  zle -N fzf-file
  bindkey '^x^f' fzf-file
  bindkey '^xf' fzf-file

  # <C-]>: src with ghq
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

  # <C-[>: git branch
  function fzf-branch () {
    if [[ ! "$BUFFER" =~ "\s*(git|tig)" ]]; then
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
  bindkey '^x^b' fzf-branch
  bindkey '^xb' fzf-branch

  # <C-r>: history
  function fzf-history() {
    local tac
    if which tac &> /dev/null; then
      tac="tac"
    else
      tac="tail -r"
    fi
  
    local selected
    selected=$(history 1 | eval $tac | fzf  --query "$LBUFFER" | awk '{$1=""; sub(/^ +/, "", $0); print $0}')
    if [ -n "$selected" ]; then
      BUFFER="${selected}"
      CURSOR=$#BUFFER
    fi
    zle reset-prompt
  }

  zle -N fzf-history
  bindkey '^r' fzf-history
fi

# =====
# Git : Completion
# =====
if (which git-numdiff &> /dev/null); then
  function _git_numdiff() {
    _git_diff $@
  }
fi

if (which git-delta &> /dev/null); then
  function _git_delta() {
    _git_diff $@
  }
fi

if (which git-lift &> /dev/null); then
  function _git_lift() {
    _git_rebase $@
  }
fi

if (which tig &> /dev/null); then
  # <C-g><C-g>: git graph powered by tig
  function git-graph() {
    </dev/tty tig
    zle reset-prompt
  }
  zle -N git-graph
  bindkey '^g^g' git-graph
  bindkey '^gg' git-graph

  # <C-g><C-s>: git status powered by tig
  function git-status() {
    </dev/tty TIG_SCRIPT=<(echo :view-status) tig
    zle reset-prompt
  }

  zle -N git-status
  bindkey '^g^s' git-status
  bindkey '^gs' git-status
fi

# vim: ft=zsh sw=2 ts=2 sts=2
