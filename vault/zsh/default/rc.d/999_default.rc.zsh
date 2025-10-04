export FPATH=$(distinct $FPATH)

for hook in ${postrc_functions[@]}; do
  if type $hook &> /dev/null; then $hook; fi
done

# vim: ft=zsh sw=2 ts=2 sts=2
