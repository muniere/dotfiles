#compdef tig

# ref: https://github.com/jonas/tig/blob/tig-2.4.1/contrib/tig-completion.zsh

# zsh completion wrapper for tig
# ==============================
#
# You need to install this script to zsh fpath with tig-completion.bash.
#
# The recommended way to install this script is to copy this and tig-completion.bash
# to '~/.zsh/_tig' and '~/.zsh/tig-completion.bash' and
# then add following to your ~/.zshrc file:
#
#  fpath=(~/.zsh $fpath)


_tig () {
  local e
  e="${HOME}/.bash.d/250.tig.bashrc"
  if [ -f $e ]; then
    . $e
  fi
}

# vim: ft=zsh sw=2 ts=2 sts=2
