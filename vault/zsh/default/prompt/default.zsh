() {
    local -A color=(
        [red]='red'
        [yellow]='yellow'
        [cyan]='cyan'
        [magenta]='magenta'
        [white]='white'
    )
    local -A symbol=(
        [LF]=$'\n'
    )

    local user="%(?.%F{$color[cyan]}.%F{$color[red]})%n%f"
    local host="%(?.%F{$color[cyan]}.%F{$color[red]})%m%f"
    local path="%F{$color[yellow]}%~%f"
    local venv="%F{$color[white]}\${venv_info_msg}%f"
    local vcs="%F{$color[magenta]}\${vcs_info_msg_0_}%f"

    export PROMPT="${user}@${host}${venv}: ${path}${symbol[LF]}%(!.#.%%) "
    export RPROMPT="${vcs}"
    export PROMPT_PROVIDER=
}
