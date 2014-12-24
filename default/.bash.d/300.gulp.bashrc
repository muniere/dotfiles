if (which gulp >/dev/null 2>&1); then
  # Usage:
  #
  # To enable bash <tab> completion for gulp, add the following line (minus the
  # leading #, which is the bash comment character) to your ~/.bashrc file:
  #
  # eval "$(gulp --completion=bash)"
  
  # Enable bash autocompletion.
  function _gulp_completions() {
    # The currently-being-completed word.
    local cur="${COMP_WORDS[COMP_CWORD]}"
    #Grab tasks
    local compls=$(gulp --tasks-simple)
    # Tell complete what stuff to show.
    COMPREPLY=($(compgen -W "$compls" -- "$cur"))
  }
  
  complete -o default -F _gulp_completions gulp
fi

# vim: ft=sh sw=2 ts=2 sts=2

