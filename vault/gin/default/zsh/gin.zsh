# =====
# gin - Git worktree wrapper
# =====

if ! command -v git &> /dev/null; then
  return
fi

# gin - Git worktree wrapper
#
# Subcommands:
#   list              List all worktrees
#   branch            List branches managed by worktrees
#   attach <branch>   Create new worktree for existing branch
#   attach -c <br>    Create new worktree with new branch
#   detach <branch>   Remove a worktree

function gin() {
  emulate -L zsh
  setopt err_return

  function _usage() {
    cat <<-EOF
	Usage: gin <command> [options]

	Commands:
	  list, ls                List all worktrees (format: path hash branch)
	  branch                  List branches managed by worktrees
	  attach [-c] <branch>    Create a worktree (with -c to create branch)
	  detach <branch>         Remove a worktree
	  rm, remove <branch>     Remove a worktree (alias for detach)
	  help [command]          Show help

	Options:
	  -h, --help              Show this help
	EOF
  }

  function _help() {
    local topic="$1"

    case "$topic" in
      ''|'-h'|'--help')
        _usage
        ;;
      'list'|'ls')
        echo "Usage: gin $topic"
        ;;
      'branch')
        echo "Usage: gin branch"
        ;;
      'attach')
        cat <<-EOF
		Usage: gin attach [-c] <branch>

		Options:
		  -c                    Create a new branch and worktree
		  -h, --help            Show this help
		EOF
        ;;
      'detach'|'rm'|'remove')
        cat <<-EOF
		Usage: gin detach <branch>

		Options:
		  -h, --help            Show this help
		EOF
        ;;
      *)
        echo "Error: unknown help topic '$topic'" >&2
        return 1
        ;;
    esac
  }

  #
  # Subcommand implementations
  #

  # List all worktrees in simple format
  function _list() {
    git worktree list --porcelain 2>/dev/null | awk '
      /^worktree / { path = substr($0, 10) }
      /^HEAD / { head = substr($0, 6) }
      /^branch / {
        branch = substr($0, 8)
        gsub(/^refs\/heads\//, "", branch)
        print path, head, branch
        path = head = branch = ""
      }
    '
  }

  # List all branch names managed by worktrees
  function _branch() {
    gin list | cut -d' ' -f3
  }

  # Prepare worktree path for a branch
  #
  # @param: branch - Branch name
  function _prepare() {
    local branch="$1"
    local repo_root
    repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || {
      echo "Error: not in a git repository" >&2
      return 1
    }

    local repo_name=$(basename "$repo_root")
    local parent_dir=$(dirname "$repo_root")
    local normalized_branch="${branch//\//-}"

    echo "${parent_dir}/${repo_name}-${normalized_branch}"
  }

  # Attach a worktree
  #
  # @option: [-c] <branch>
  #   -c: Create new branch and worktree
  function _attach() {
    local create_branch=0
    local branch=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
      case "$1" in
        '-c')
          create_branch=1
          shift
          ;;
        '-h'|'--help')
          cat <<-EOF
		Usage: gin attach [-c] <branch>

		Options:
		  -c                    Create a new branch and worktree
		  -h, --help            Show this help
		EOF
          return 0
          ;;
        -*)
          echo "Error: unknown option '$1'" >&2
          return 1
          ;;
        *)
          if [[ -n "$branch" ]]; then
            echo "Error: unexpected argument '$1'" >&2
            return 1
          fi
          branch="$1"
          shift
          ;;
      esac
    done

    if [[ -z "$branch" ]]; then
      cat >&2 <<-EOF
		Error: branch name required
		Usage: gin attach [-c] <branch>
		EOF
      return 1
    fi

    local existing_worktree_path
    existing_worktree_path=$(gin list | awk -v branch="$branch" '$3 == branch { print $1; exit }')
    if [[ -n "$existing_worktree_path" ]]; then
      echo "Error: worktree already exists for branch '$branch' at '$existing_worktree_path'" >&2
      return 1
    fi

    local target_path
    target_path=$(_prepare "$branch") || return 1

    if [[ $create_branch -eq 1 ]]; then
      git worktree add "$target_path" -b "$branch" || {
        echo "Error: failed to create worktree" >&2
        return 1
      }
    else
      git worktree add "$target_path" "$branch" || {
        echo "Error: failed to create worktree" >&2
        return 1
      }
    fi

    echo "Created worktree: $target_path"
  }

  # Detach a worktree
  #
  # @param branch
  function _detach() {
    local branch="$1"

    if [[ "$branch" == "-h" || "$branch" == "--help" ]]; then
      cat <<-EOF
		Usage: gin detach <branch>

		Options:
		  -h, --help            Show this help
		EOF
      return 0
    fi

    if [[ "$branch" == -* ]]; then
      echo "Error: unknown option '$branch'" >&2
      return 1
    fi

    if [[ $# -gt 1 ]]; then
      echo "Error: unexpected argument '$2'" >&2
      return 1
    fi

    if [[ -z "$branch" ]]; then
      cat >&2 <<-EOF
		Error: branch name required
		Usage: gin detach <branch>
		EOF
      return 1
    fi

    # Find worktree for branch
    local worktree_path
    worktree_path=$(gin list | awk -v branch="$branch" '$3 == branch { print $1; exit }')

    if [[ -z "$worktree_path" ]]; then
      echo "Error: no worktree found for branch '$branch'" >&2
      return 1
    fi

    git worktree remove "$worktree_path"
  }

  #
  # Main
  #

  if [[ $# -eq 0 ]]; then
    _usage >&2
    return 1
  fi

  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    _usage
    return 0
  fi

  local subcommand="$1"
  shift

  case "$subcommand" in
    'list' | 'ls')
      if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        echo "Usage: gin $subcommand"
        return 0
      fi
      if [[ $# -gt 0 ]]; then
        echo "Error: unexpected argument '$1'" >&2
        return 1
      fi
      _list "$@"
      ;;
    'branch')
      if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        echo "Usage: gin branch"
        return 0
      fi
      if [[ $# -gt 0 ]]; then
        echo "Error: unexpected argument '$1'" >&2
        return 1
      fi
      _branch "$@"
      ;;
    'attach')
      _attach "$@"
      ;;
    'detach')
      _detach "$@"
      ;;
    'rm' | 'remove')
      _detach "$@"
      ;;
    'help')
      if [[ $# -gt 1 ]]; then
        echo "Error: unexpected argument '$2'" >&2
        return 1
      fi
      _help "$1"
      ;;
    *)
      cat >&2 <<-EOF
		Error: unknown command '$subcommand'
		Run 'gin' without arguments for usage
		EOF
      unfunction _usage _help _list _branch _attach _detach _prepare
      return 1
      ;;
  esac

  # Cleanup local functions
  unfunction _usage _help _list _branch _attach _detach _prepare
}

# vim: ts=4 sw=4 sts=4 list
