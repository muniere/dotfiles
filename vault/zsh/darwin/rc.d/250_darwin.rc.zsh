# zsh-completions
if [ -d $HOMEBREW_PREFIX/share/zsh-completions ]; then
  export FPATH="$HOMEBREW_PREFIX/share/zsh-completions:$FPATH"
fi

# other completions
if [ -d $HOMEBREW_PREFIX/share/zsh/site-functions ]; then
  export FPATH="$HOMEBREW_PREFIX/share/zsh/site-functions:$FPATH"
fi

# vim: ft=zsh sw=2 ts=2 sts=2
