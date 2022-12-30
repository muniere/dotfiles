# =====
# asdf : Completion
# =====
if [ -f $HOMEBREW_PREFIX/opt/asdf/libexec/asdf.sh ]; then
  source $HOMEBREW_PREFIX/opt/asdf/libexec/asdf.sh
fi

# =====
# Google Cloud : Completion
# ===
if [ -d $HOMEBREW_PREFIX/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/ ]; then
  source "$HOMEBREW_PREFIX/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.zsh.inc"
  source "$HOMEBREW_PREFIX/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/completion.zsh.inc"
fi

# vim: ft=zsh sw=2 ts=2 sts=2
