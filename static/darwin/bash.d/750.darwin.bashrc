# =====
# asdf : Completion
# =====
if (which asdf &> /dev/null); then
  source /usr/local/opt/asdf/asdf.sh
fi

# =====
# Google Cloud : Completion
# =====
if [ -d /usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/ ]; then
  source "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc"
  source "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/completion.bash.inc"
fi

# =====
## Tig : Completion
# =====
if [ -f /usr/local/opt/tig/etc/bash_completion.d/tig-completion.bash ]; then
  . /usr/local/opt/tig/etc/bash_completion.d/tig-completion.bash 
fi

# vim: ft=sh sw=2 ts=2 sts=2
