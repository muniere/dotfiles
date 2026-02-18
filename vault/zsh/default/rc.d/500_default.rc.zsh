# =====
# Zsh : Hooks
# =====
function _histignore_hook() { 
  emulate -L zsh

  if [[ ${1%%$'\n'} =~ ${~HISTORY_IGNORE} ]]; then
    # hit: return 1; DO NOT push to history
    return 1
  else 
    # miss: return 0; DO push to history 
    return 0
  fi
} 

zshaddhistory_functions+=(_histignore_hook)

##
# Invalidate completion cache when fpath changed
#
# This hook will be used as a part of precmd_functions.
##
function _fpath_hook() {
  # Global cache memory
  typeset -g _fpath_ghost

  local ghost="${_fpath_ghost}"

  # Init at first time
  if [[ -z $ghost ]]; then
    _fpath_ghost="$FPATH"
    return 0
  fi

  # Noop when not changed
  if [[ "$FPATH" == "$ghost" ]]; then
    return 0
  fi

  _fpath_ghost="$FPATH"
  autoload -Uz compinit
  compinit -u
  echo "fpath: compinit" >&2
}

# NOTE: here needs to register as postrc_functions too,
#       in order to initialize `_fpath_ghost`.
precmd_functions+=(_fpath_hook)
postrc_functions+=(_fpath_hook)

##
# Configure prompt info before each prompt rendering
#
# This hook will be used as a part of precmd_functions.
##
function _prompt_hook() {
  # Skip if using custom prompt provider
  if [ -n "$PROMPT_PROVIDER" ]; then return; fi

  # Export VCS info
  LANG=C vcs_info

  # Export Python virtualenv info
  LANG=C venv_info
}

precmd_functions+=(_prompt_hook)

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
export ZLE_RPROMPT_INDENT=0

autoload -Uz vcs_info
setopt prompt_subst
setopt transient_rprompt
zstyle ':vcs_info:*' formats '[%b]'
zstyle ':vcs_info:*' actionformats '[%b|%a]'

export ZSH_PROMPT_DIR="$XDG_DATA_HOME/zsh/prompt"
export ZSH_PROMPT_THEME="default"

if [ -f "$ZSH_PROMPT_DIR/zprompt.zsh" ]; then
  source "$ZSH_PROMPT_DIR/zprompt.zsh"
fi

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
setopt inc_append_history

# =====
# Zsh : Keys
# =====
bindkey -d
bindkey -e

for x in {!..~}; do 
  bindkey -r "^[${x}"
  bindkey -r "^[^${x}"
  bindkey -r "^[O${x}"
  bindkey -r "^X${x}"
  bindkey -r "^X^${x}"
done

autoload history-search-end
zle -N history-beginning-search-backward-end history-search-end
zle -N history-beginning-search-forward-end history-search-end
bindkey "^P" history-beginning-search-backward-end
bindkey "^N" history-beginning-search-forward-end 
bindkey "^[[Z" reverse-menu-complete
bindkey -r "^S"
bindkey -r "^G"

# =====
# Zsh : Time
# =====
TIMEFMT=$'\nreal\t%E\nuser\t%U\nsys\t%S'

# =====
# direnv : Completion
# =====
if command -v direnv &> /dev/null; then
  eval "$(direnv hook zsh)"
fi

# =====
# fzf : Binding
# =====

if command -v fzf &> /dev/null; then
  # <C-x><C-f>: find file
  function fzf-file () {
    local selected
    if command -v fd &> /dev/null; then
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

  # <C-x><C-b>: git branch
  function fzf-branch () {
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
    if command -v tac &> /dev/null; then
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
if command -v git-numdiff &> /dev/null; then
  function _git_numdiff() {
    _git_diff $@
  }
fi

if command -v git-delta &> /dev/null; then
  function _git_delta() {
    _git_diff $@
  }
fi

if command -v git-lift &> /dev/null; then
  function _git_lift() {
    _git_rebase $@
  }
fi

if command -v git-gtr &> /dev/null; then
  zstyle ':completion:*:*:git:*' user-commands gtr:'Git worktree management'
  autoload -Uz _gtr
  compdef _gtr gtr

  alias gat=gtr

  if command -v fzf &> /dev/null; then
    # <C-x><C-t>: git worktreee branch
    function fzf-worktree-branch() {
      local selected
      selected=$(gtr list --porcelain 2>/dev/null | awk '{print $2}' | fzf)

      if [ -n "$selected" ]; then
        BUFFER="${BUFFER}${selected}"
        CURSOR=$#BUFFER
      fi
      zle reset-prompt
    }

    zle -N fzf-worktree-branch
    bindkey '^x^t' fzf-worktree-branch
    bindkey '^xt' fzf-worktree-branch
  fi
fi

if command -v tig &> /dev/null; then
  # <C-g><C-g>: git status powered by tig
  function git-status() {
    </dev/tty TIG_SCRIPT=<(echo :view-status) tig
    zle reset-prompt
  }

  zle -N git-status
  bindkey '^g^g' git-status
  bindkey '^gg' git-status
fi

# =====
# Python
# =====

## venv_info - provide virtual env information
##
## This functions inspires `vcs_info` and `VCS_INFO_set`
function venv_info() {
  local format=" (%s)"

  typeset -g venv_info_msg=

  if [ -n "$VIRTUAL_ENV" ]; then
    typeset -g venv_info_msg="$(printf "$format" "$(basename $VIRTUAL_ENV)")"
  fi
}

# vim: ft=zsh sw=2 ts=2 sts=2
