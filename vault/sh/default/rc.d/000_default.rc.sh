function distinct() {
  if [ -n "$ZSH_VERSION" ]; then
    setopt localoptions shwordsplit
  fi

  local arg1="$1"
  local arg2="$2"

  local sep=${arg2:=:}
  local words=${arg1//$sep/ }

  local xs=""
  for x in $words; do 
    if [[ ":$xs:" == *":$x:"* ]]; then
      : # do nothing if already exists
    else
      xs="$xs:$x"
    fi
  done

  xs="${xs/#:/}"
  xs="${xs/%:/}"

  echo $xs
}

export LC_ALL=C
export LANG=en_US.UTF-8
export EDITOR=vim

export PATH="/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export PATH="/usr/local/bin:/usr/local/sbin:$PATH"

# Disable control flow by Ctrl-S and Ctrl-Q
[ -t 0 ] && stty -ixon

# vim: ft=sh sw=2 ts=2 sts=2
