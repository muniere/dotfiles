bindkey -e

## Funcitons {{{1

function zshaddhistory() { # {{{2
  local line=${1%%$'\n'}
  local cmd=${line%% *}

  [[ ${#line} -ge 5 ]]
} # }}}

function update_title() { # {{{2
  if (echo $TERM | grep -i "xterm" 2>&1 >/dev/null); then
    title="${PWD/$HOME/~}"
    echo -ne "\033]0;${title}\007"
  fi
} # }}}

function update_vcs() { # {{{2
  psvar=()
  LANG=en_US.UTF-8 vcs_info
  psvar[1]="$vcs_info_msg_0_"
} # }}}

function precmd() { # {{{2
  update_title
  update_vcs
} # }}}

#
# Override sudo
#
function sudo() { # {{{2
  local args
  case $1 in
    # `sudo vim path1 path2 ...` => `vim sudo:path1 sudo:path2 ...`
    vi|vim)
      args=()
      for arg in $@[2,-1]
      do
        if [ $arg[1] = '-' ]; then
          args[$(( 1+$#args ))]=$arg
        else
          args[$(( 1+$#args ))]="sudo:$arg"
        fi
      done
      command vim $args
      ;;
    *)
      command sudo $@
      ;;
  esac
} # }}}

## }}}

### Completion {{{1
autoload -Uz colors; colors
autoload -Uz compinit; compinit
setopt auto_menu
setopt autopushd
setopt list_packed
setopt list_types
setopt magic_equal_subst
setopt noautoremoveslash
setopt nonomatch
setopt print_eight_bit
setopt pushd_ignore_dups
zstyle ':completion:*:default' menu select=2
zstyle ':completion:*:sudo:*' command-path /usr/local/sbin /usr/local/bin /usr/sbin /usr/bin /sbin /bin
### }}}

### Prompt {{{1
autoload -Uz vcs_info
setopt prompt_subst
setopt transient_rprompt
zstyle ':vcs_info:*' formats '[%b]'
zstyle ':vcs_info:*' actionformats '[%b|%a]'
PROMPT='%(?.%F{cyan}.%F{red})%n%f@%(?.%F{cyan}.%F{red})%m%f: %F{yellow}%~%f
%(!.#.%%) '
RPROMPT='%1(v|%F{magenta}%1v%f|)'
### }}}

### History  {{{1
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
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
bindkey "^[[Z" reverse-menu-complete
### }}}

### Time {{{1
TIMEFMT=$'\nreal\t%E\nuser\t%U\nsys\t%S'
### }}}

# vim: ft=zsh sw=2 ts=2 sts=2
