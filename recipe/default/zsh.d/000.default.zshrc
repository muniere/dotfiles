function addfpath() {
  # delete duplicated path
  local args="$@"
  local base=$FPATH
  for x in $args; do
    base=${base//$x/}
    base=${base//::/:}
  done

  # add new path
  local ext="${args// /:}"

  export FPATH="$ext:$base"
}
