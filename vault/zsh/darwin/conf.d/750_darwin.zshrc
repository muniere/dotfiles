# =====
# Google Cloud : Completion
# ===
if [ -f $HOMEBREW_PREFIX/share/google-cloud-sdk/path.zsh.inc ]; then
  source $HOMEBREW_PREFIX/share/google-cloud-sdk/path.zsh.inc
fi
if [ -f $HOMEBREW_PREFIX/share/google-cloud-sdk/completion.zsh.inc ]; then
  source $HOMEBREW_PREFIX/share/google-cloud-sdk/completion.zsh.inc
fi

# =====
# Zsh : Syntax Highlighting
# =====
if [ -f $HOMEBREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]; then
  source $HOMEBREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh 
fi

# =====
# Zsh : Auto Suggestions
# =====
if [ -f $HOMEBREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh ]; then
  source $HOMEBREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh 
  ZSH_AUTOSUGGEST_STRATEGY=(history completion)
fi

# vim: ft=zsh sw=2 ts=2 sts=2
