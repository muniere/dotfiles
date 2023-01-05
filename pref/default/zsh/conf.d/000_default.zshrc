function addfpath() {
  argv=("$@")

  for ((i=${#argv[@]}; i > 0; i--)); do
    x=${argv[i]}

    if [[ ":$FPATH:" == *":$x:"* ]]; then
      export FPATH="$x:${FPATH//:$x:/:}"
    else
      export FPATH="$x:$FPATH"
    fi
  done
}

# vim: ft=sh sw=2 ts=2 sts=2
