function addfpath() {
  local x=$1
  local xs=":$FPATH:"
  xs="${xs//:$x:/:}"
  xs="${xs/#:/}"
  xs="${xs/%:/}"
  export FPATH="$x:$xs"
}

# vim: ft=sh sw=2 ts=2 sts=2
