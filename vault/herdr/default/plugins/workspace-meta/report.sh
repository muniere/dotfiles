#!/bin/sh

# NAME
#   report.sh - Report sidebar tokens for every herdr workspace
#
# SYNOPSIS
#   report.sh
#
# DESCRIPTION
#   Run by herdr as the startup and event hook of the workspace-meta plugin.
#   Space rows in the sidebar have no built-in token for tabs, so this reports
#   them as workspace metadata, for ui.sidebar.spaces.rows to show:
#
#     $tabs  the named tabs' labels, in order  タブA / タブB
#
#   When the workspace name starts with an emoji, the value is indented by 3
#   cells to line up with the text after it, as in "🔧 name".
#
#   A workspace with no named tab shows its Git branch instead, read as herdr
#   reads its own branch token: from the cwd of the first tab's first pane. It
#   is refreshed on tab events only, so a checkout shows on the next one.
#
#   herdr trims whitespace around token values, so the indent starts with a
#   braille blank (U+2800), which is not whitespace but shows as one.
#
#   Every workspace is refreshed on each event rather than only the one in the
#   event payload: it costs one list call, and it cannot miss a workspace whose
#   tabs moved elsewhere. herdr caps token values at 80 characters.
#
# SEE ALSO
#   https://herdr.dev/docs/plugins/
#   https://herdr.dev/docs/configuration/#sidebar-row-layouts

herdr="${HERDR_BIN_PATH:-herdr}"
command -v jq >/dev/null 2>&1 || exit 0

workspaces="$("$herdr" workspace list 2>/dev/null)" || workspaces='{}'
tabs="$("$herdr" tab list 2>/dev/null)" || exit 0
panes="$("$herdr" pane list 2>/dev/null)" || panes='{}'

# One line per workspace: ID, whether to indent, joined tab labels, and the cwd
# of its first tab's first pane, separated by US (0x1f); labels and paths hold
# no control characters. Unnamed tabs, whose default label is just a number,
# are left out.
printf '%s\n%s\n%s\n' "$workspaces" "$tabs" "$panes" | jq -rs '
  (.[0].result.workspaces // [] | map({(.workspace_id): .label}) | add // {}) as $names
  | (.[2].result.panes // []) as $panes
  | .[1].result.tabs // []
  | group_by(.workspace_id)[]
  | .[0].tab_id as $first
  | [ .[0].workspace_id,
      (if ($names[.[0].workspace_id] // "" | test("^\\p{Extended_Pictographic}")) then "1" else "" end),
      (map(.label | select(test("^[0-9]+$") | not)) | join(" / ")),
      ([$panes[] | select(.tab_id == $first) | .cwd][0] // "")
    ]
  | join("\u001f")' 2>/dev/null \
  | while IFS="$(printf '\037')" read -r wid indent labels cwd; do
      # Fall back to the branch; with neither, the empty value clears the token.
      if [ -z "$labels" ] && [ -n "$cwd" ]; then
        labels="$(git -C "$cwd" symbolic-ref --short -q HEAD 2>/dev/null)"
      fi
      [ -n "$labels" ] && [ -n "$indent" ] && labels="$(printf '\342\240\200')  ${labels}"
      "$herdr" workspace report-metadata "$wid" \
        --source muniere.workspace-meta --token "tabs=${labels}" >/dev/null 2>&1
    done
exit 0
