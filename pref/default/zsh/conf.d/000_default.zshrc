function addfpath() {
  # delete duplicate path
  local base=$FPATH
  for x in "$@"; do
    base=${base//$x/}
    base=${base//::/:}
  done

  # add new path
  export FPATH="${*// /:}:$base"
}

# vim: ft=sh sw=2 ts=2 sts=2
