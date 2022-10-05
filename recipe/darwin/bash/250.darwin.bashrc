# Completion
if [ -f $BREW_PREFIX/etc/bash_completion ]; then
  source $BREW_PREFIX/etc/bash_completion
fi
if [ -f $BREW_PREFIX/share/bash-completion/bash_completion ]; then
  source $BREW_PREFIX/share/bash-completion/bash_completion
fi

# vim: ft=sh sw=2 ts=2 sts=2
