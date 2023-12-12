bindkey -e

# =====
# Zsh : Hooks
# =====
function zshaddhistory() { 
  local line=${1%%$'\n'}
  local cmd=${line%% *}

  [[ ${#line} -ge 5 
      && ${cmd} != (l) 
      && ${cmd} != (ls) 
      && ${cmd} != (la) 
      && ${cmd} != (ll) 
      && ${cmd} != (cd) 
      && ${cmd} != (rm) 
      && ${cmd} != (man) 
      && ${cmd} != (git) 
      && ${cmd} != (tig) 
  ]]
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
HISTSIZE=100000
SAVEHIST=100000
setopt hist_ignore_all_dups
setopt hist_ignore_dups
setopt hist_ignore_space
setopt hist_reduce_blanks
setopt share_history
setopt extended_history
setopt combining_chars

autoload history-search-end
zle -N history-beginning-search-backward-end history-search-end
zle -N history-beginning-search-forward-end history-search-end
bindkey "^P" history-beginning-search-backward-end
bindkey "^N" history-beginning-search-forward-end 
bindkey "\e[Z" reverse-menu-complete

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

# <C-x><C-f>: find file
if (which fzf-file &> /dev/null); then
  zle -N fzf-file
  bindkey '^x^f' fzf-file
fi

# <C-]>: src with ghq
if (which fzf-src &> /dev/null); then
  zle -N fzf-src
  bindkey '^]' fzf-src
fi

# <C-@>: git log
if (which fzf-gitlog &> /dev/null); then
  zle -N fzf-gitlog
  bindkey '^x^l' fzf-gitlog
fi

# <C-[>: git branch
if (which fzf-branch &> /dev/null); then
  zle -N fzf-branch
  bindkey '^x^b' fzf-branch
fi

# <C-r>: history
if (which fzf-history &> /dev/null); then
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

# vim: ft=zsh sw=2 ts=2 sts=2
