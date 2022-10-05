# zsh-completions
if [ -d $BREW_PREFIX/share/zsh-completions ]; then
  addfpath $BREW_PREFIX/share/zsh-completions
fi

# other completions
if [ -d $BREW_PREFIX/share/zsh/site-functions ]; then
  addfpath $BREW_PREFIX/share/zsh/site-functions
fi

# vim: ft=zsh sw=2 ts=2 sts=2
