# =====
# Bash : Functions
# =====

# update terminal title 
function __title {
  echo "\033]0;${PWD/$HOME/~}\007"
}

# colorize default
function __color0 {
  echo "\033[0m"
}

# colorize usename and hostname
function __color1 {
  if [ $# -le 0 ]; then
    echo -en "\033[36m"
  elif [ $1 -eq 0 ]; then 
    echo -en "\033[36m"
  else 
    echo -en "\033[31m"
  fi
}

# colorize path
function __color2 {
  if [ $# -le 0 ]; then 
    echo -en "\033[33m"
  elif [ $1 -eq 0 ]; then 
    echo -en "\033[33m"
  else 
    echo -en "\033[31m"
  fi
}

# colorize vcs_info
function __color3 {
  if [ $# -le 0 ]; then 
    echo -en "\033[35m"
  elif [ $1 -eq 0 ]; then 
    echo -en "\033[35m"
  else 
    echo -en "\033[31m"
  fi
}

# ====
# Bash : Completion
# ====
if [ -d $XDG_DATA_HOME/bash/bash_completion.d ]; then
  for f in $XDG_DATA_HOME/bash/bash_completion.d/*; do
    source $f
  done
fi

# =====
# Bash : Prompt
# =====
if [ -f "$STARSHIP_CONFIG" ] && (which starship &>/dev/null); then
  eval "$(starship init bash)"
  export PROMPT_PROVIDER="starship"
elif (type __git_ps1 &> /dev/null); then
  export GIT_PS1_SHOWDIRTYSTATE=true
  export PROMPT_COMMAND='status=$?; echo -ne "$(__title)";PS1="$(__color0)[$(__color1 $status)\u$(__color0)@$(__color1 $status)\h$(__color0): $(__color2)\w$(__color0)$(__color3)$(__git_ps1)$(__color0)]\n\$ "'
  export PROMPT_PROVIDER=
else 
  export PROMPT_COMMAND='status=$?; echo -ne "$(__title)";PS1="$(__color0)[$(__color1 $status)\u$(__color0)@$(__color1 $status)\h$(__color0): $(__color2)\w$(__color0)]\n\$ "'
  export PROMPT_PROVIDER=
fi

set show-all-if-ambiguous on
set completion-ignore-case on

# =====
# Bash : History
# =====
if [ -n "$XDG_CONFIG_HOME" ]; then
  export HISTFILE=$XDG_CONFIG_HOME/bash/.bash_history
else
  export HISTFILE=$HOME/.config/bash/.bash_history
fi

export HISTCONTROL=erasedups:ignoreboth
export HISTSIZE=10000
export HISTTIMEFORMAT='%Y/%m/%d %T:$ '
shopt -s histappend
shopt -s checkwinsize

# =====
# direnv : Hook
# =====
if (which direnv &> /dev/null); then
  eval "$(direnv hook bash)"
fi

# vim: ft=sh sw=2 ts=2 sts=2
