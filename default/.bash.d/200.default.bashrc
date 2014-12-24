# .bashrc for all

## History
export HISTCONTROL=erasedups:ignoreboth
export HISTSIZE=10000
export HISTTIMEFORMAT='%Y/%m/%d %T:$ '
shopt -s histappend
shopt -s checkwinsize

function _color1 {
  if [ $# -le 0 ]; then
    echo -en "\033[36m"
  elif [ $1 -eq 0 ]; then 
    echo -en "\033[36m"
  else 
    echo -en "\033[31m"
  fi
}

function _color2 {
  if [ $# -le 0 ]; then 
    echo -en "\033[33m"
  elif [ $1 -eq 0 ]; then 
    echo -en "\033[33m"
  else 
    echo -en "\033[31m"
  fi
}

function _reset {
  echo "\033[0m"
}

function _title {
  echo "\033]0;${PWD/$HOME/~}\007"
}

## Prompt
export PROMPT_COMMAND='status=$?; echo -ne "`_title`";PS1="`_reset`[`_color1 $status`\u`_reset`@`_color1 $status`\h`_reset`: `_color2`\w`_reset`]\n\$ "'

set show-all-if-ambiguous on
set completion-ignore-case on

# vim: ft=sh sw=2 ts=2 sts=2
