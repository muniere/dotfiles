if [ -d $HOME/.anyenv/bin ]; then
  addpath $HOME/.anyenv/bin
  eval "$(anyenv init - zsh)"
fi

# vim: ft=sh sw=2 ts=2 sts=2
