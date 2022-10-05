# =====
# asdf : Completion
# =====
if (which asdf &> /dev/null); then
  source $BREW_PREFIX/opt/asdf/asdf.sh
fi

# =====
# Google Cloud : Completion
# ===
if [ -d $BREW_PREFIX/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/ ]; then
  source "$BREW_PREFIX/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.zsh.inc"
  source "$BREW_PREFIX/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/completion.zsh.inc"
fi

# vim: ft=zsh sw=2 ts=2 sts=2
