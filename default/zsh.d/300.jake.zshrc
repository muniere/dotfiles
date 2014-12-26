if (type compdef &>/dev/null); then
  function _jake() {
    if [ -f Jakefile ]||[ -f jakefile ]; then
    compadd `jake -T | cut -d " " -f 2 | sed -E "s/.\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g"`
    fi
  }
  compdef _jake jake
fi

# vim: ft=zsh sw=2 ts=2 sts=2
