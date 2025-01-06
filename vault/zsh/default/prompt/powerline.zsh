() {
    local -A color=(
        [green]='22'
        [lime]='154'
        [rose]='160'
        [magenta]='165'
        [orange]='166'
        [black]='232'
        [white]='255'
    )
    local -A symbol=(
        [ZH]=''
        [ZL]=''
        [LF]=$'\n'
    )

    local info1_fmt=' %B%n@%m%b '
    local info1_ok="%K{$color[lime]}%F{$color[green]}${info1_fmt}%f%k%K{$color[orange]}%F{$color[lime]}${symbol[ZL]}%f%k"
    local info1_ng="%K{$color[rose]}%F{$color[white]}${info1_fmt}%f%k%K{$color[orange]}%F{$color[rose]}${symbol[ZL]}%f%k"
    local info1="%(?.${info1_ok}.${info1_ng})"

    local info2_fmt=' %B%~%b '
    local info2="%K{$color[orange]}%F{$color[white]}${info2_fmt}%f%k%F{$color[orange]}${symbol[ZL]}%f%k"

    local vcs="%F{$color[magenta]}\${vcs_info_msg_0_}%f"

    export PROMPT="${info1}${info2}${symbol[LF]}%(!.#.%%) "
    export RPROMPT="${vcs}"
    export PROMPT_PROVIDER=
}
