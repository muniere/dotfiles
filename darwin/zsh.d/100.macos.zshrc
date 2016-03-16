# homebrew
if [ -d /usr/local/Library/Contributions ]; then
  fpath=(/usr/local/Library/Contributions $fpath)
fi

# zsh-completions
if [ -d /usr/local/share/zsh-completions ]; then
  fpath=(/usr/local/share/zsh-completions $fpath)
fi

# other completions
if [ -d /usr/local/share/zsh/site-functions ]; then
  fpath=(/usr/local/share/zsh/site-functions $fpath)
fi

# vim: ft=zsh sw=2 ts=2 sts=2
