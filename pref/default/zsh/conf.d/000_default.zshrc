function addfpath() {
  local x=$1

  if [[ ":$FPATH:" == *":$x:"* ]]; then
    export FPATH="$x:${FPATH//:$x:/:}"
  else
    export FPATH="$x:$FPATH"
  fi
}

# vim: ft=sh sw=2 ts=2 sts=2
