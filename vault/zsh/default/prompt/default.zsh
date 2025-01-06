() {
    local user='%(?.%F{cyan}.%F{red})%n%f'
    local host='%(?.%F{cyan}.%F{red})%m%f'
    local path='%F{yellow}%~%f'
    local venv='%F{white}${venv_info_msg}%f'
    local vcs='%F{magenta}${vcs_info_msg_0_}%f'
    local LF=$'\n'

    export PROMPT="${user}@${host}${venv}: ${path}${LF}%(!.#.%%) "
    export RPROMPT="${vcs}"
    export PROMPT_PROVIDER=
}
