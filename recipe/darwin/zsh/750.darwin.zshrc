# =====
# asdf : Completion
# =====
if (which asdf &> /dev/null); then
  source $BREW_PREFIX/opt/asdf/asdf.sh
fi

# =====
# Google Cloud : Completion
# ===
if [ -d /usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/ ]; then
  source "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.zsh.inc"
  source "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/completion.zsh.inc"
fi

# =====
# Tig : Completion
# =====
if [ -f $BREW_PREFIX/opt/tig/etc/bash_completion.d/tig-completion.bash ]; then
  . $BREW_PREFIX/opt/tig/etc/bash_completion.d/tig-completion.bash 
fi


# vim: ft=zsh sw=2 ts=2 sts=2
