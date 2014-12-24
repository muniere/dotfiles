if (type compdef &>/dev/null); then
  function _gibo() {
    compadd $( find $HOME/.gitignore-boilerplates -name "*.gitignore" -exec basename \{\} .gitignore \; )
  }
  compdef _gibo gibo
fi

# vim: ft=zsh sw=2 ts=2 sts=2
