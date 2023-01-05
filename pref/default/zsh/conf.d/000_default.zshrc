function addfpath() {
  argv=("$@")

  if [ -n "$ZSH_VERSION" ]; then
    setopt localoptions ksharrays
  fi

  for ((i=${#argv[@]} - 1; i >= 0; i--)); do
    x=${argv[i]}

    if [[ ":$FPATH:" == *":$x:"* ]]; then
      export FPATH="$x:${FPATH//:$x:/:}"
    else
      export FPATH="$x:$FPATH"
    fi
  done
}

# vim: ft=sh sw=2 ts=2 sts=2
