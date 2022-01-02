if (which git-numstat &> /dev/null); then
  function _git_numstat() {
    _git_diff $@
  }
fi

# vim: ft=sh sw=2 ts=2 sts=2
