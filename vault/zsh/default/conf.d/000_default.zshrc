function prompter() {
    local style="$1"
    case "$1" in
        powerline) __prompter_powerline;;
        default) __prompter_default;;
        *) __prompter_default;;
    esac
}

function __prompter_powerline() {
    local green='22'
    local lime='154'
    local rose='160'
    local magenta='165'
    local orange='166'
    local black='232'
    local white='255'
    local ZH=''
    local ZL=''
    local LF=$'\n'

    local info1_fmt=' %B%n@%m%b '
    local info1_ok="%K{$lime}%F{$green}${info1_fmt}%f%k%K{$orange}%F{$lime}${ZL}%f%k"
    local info1_ng="%K{$rose}%F{$white}${info1_fmt}%f%k%K{$orange}%F{$rose}${ZL}%f%k"
    local info1="%(?.${info1_ok}.${info1_ng})"

    local info2_fmt=' %B%~%b '
    local info2="%K{$orange}%F{$white}${info2_fmt}%f%k%F{$orange}${ZL}%f%k"

    local vcs="%F{magenta}${vcs_info_msg_0_}%f"

    PROMPT="${info1}${info2}${LF}%(!.#.%%) "
    RPROMPT="${vcs}"
}

function __prompter_default() {
    local user='%(?.%F{cyan}.%F{red})%n%f'
    local host='%(?.%F{cyan}.%F{red})%m%f'
    local path='%F{yellow}%~%f'
    local venv='%F{white}${venv_info_msg}%f'
    local vcs='%F{magenta}${vcs_info_msg_0_}%f'
    local LF=$'\n'

    PROMPT="${user}@${host}${venv}: ${path}${LF}%(!.#.%%) "
    RPROMPT="${vcs}"
}

# vim: ft=zsh sw=2 ts=2 sts=2
