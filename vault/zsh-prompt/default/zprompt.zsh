##
# Change prompt theme for zsh
#
# NOTE: This function cannot be defined as isolated script,
#       because it needs to run `source` to affect to current shell.
##
function chprompt() {
  local theme="${1:-$ZSH_PROMPT_THEME}"
  if [ -z "$theme" ]; then
    echo "Usage: chprompt <theme>" >&2
    return 1
  fi

  local home="${XDG_DATA_HOME:-$HOME/.local/share}"
  local dir="${ZSH_PROMPT_DIR:-$home/zsh/prompt}"
  local path="$dir/themes/$theme.zsh"
  if [ ! -f "$path" ]; then
    echo "File not found: $path" >&2
    return 1
  fi

  source "$path"
}

chprompt "${ZSH_PROMPT_THEME:-default}"
