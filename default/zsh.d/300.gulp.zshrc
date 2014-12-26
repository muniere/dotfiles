if (which gulp >/dev/null 2>&1); then
  # Usage:
  #
  # To enable zsh <tab> completion for gulp, add the following line (minus the
  # leading #, which is the zsh comment character) to your ~/.zshrc file:
  #
  # eval "$(gulp --completion=zsh)"
  
  # Enable zsh autocompletion.
  function _gulp_completion() {
    # Grab tasks
    compls=$(gulp --tasks-simple)
    completions=(${=compls})
    compadd -- $completions
  }
  
  compdef _gulp_completion gulp
fi

# vim: ft=sh sw=2 ts=2 sts=2

