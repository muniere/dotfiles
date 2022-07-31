# zsh-completions
if [ -d /usr/local/share/zsh-completions ]; then
  addfpath /usr/local/share/zsh-completions
fi

# other completions
if [ -d /usr/local/share/zsh/site-functions ]; then
  addfpath /usr/local/share/zsh/site-functions
fi

# vim: ft=zsh sw=2 ts=2 sts=2
