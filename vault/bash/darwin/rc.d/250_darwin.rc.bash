# Completion
if [ -f $HOMEBREW_PREFIX/etc/bash_completion ]; then
  source $HOMEBREW_PREFIX/etc/bash_completion
fi
if [ -f $HOMEBREW_PREFIX/share/bash-completion/bash_completion ]; then
  source $HOMEBREW_PREFIX/share/bash-completion/bash_completion
fi

# vim: ft=sh sw=2 ts=2 sts=2
