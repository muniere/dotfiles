if (which git-delta &> /dev/null); then
  function _git_delta() {
    _git_diff $@
  }
fi

# vim: ft=sh sw=2 ts=2 sts=2
