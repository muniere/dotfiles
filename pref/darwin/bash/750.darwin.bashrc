# =====
# asdf : Completion
# =====
if (which asdf &> /dev/null); then
  source $HOMEBREW_PREFIX/opt/asdf/asdf.sh
fi

# =====
# Google Cloud : Completion
# =====
if [ -d $HOMEBREW_PREFIX/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/ ]; then
  source $HOMEBREW_PREFIX/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc
  source $HOMEBREW_PREFIX/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/completion.bash.inc
fi

# =====
## Tig : Completion
# =====
if [ -f $HOMEBREW_PREFIX/etc/bash_completion.d/tig-completion.bash ]; then
  . $HOMEBREW_PREFIX/etc/bash_completion.d/tig-completion.bash
fi

# vim: ft=sh sw=2 ts=2 sts=2
