#!/usr/bin/env bash
# Rename this herdr workspace (and tab) to a Japanese title for the session.
# Custom hook, installed beside the herdr-managed herdr-agent-state.sh. Wired as a
# global UserPromptSubmit hook (async). On each prompt it summarizes the session
# — its opening request, the recent conversation, and the new prompt — into a
# short "<emoji> label", and renames the workspace (and tab) only when the
# session's theme actually changed. Best-effort: silently no-ops whenever
# anything is missing or we are not inside herdr.
#
# A name the user gave by hand is never overwritten. herdr does not record who
# set a label (its custom_name is filled by API renames too), so this hook keeps
# its own marker: the label it last set, per session and workspace. A label that
# differs from the marker was set by someone else.

# The summarizer below spawns `claude -p`, whose own prompt would fire this hook
# again. The child runs with HERDR_RENAME=1 (set below), so any nested invocation
# returns at once.
[ "${HERDR_RENAME:-}" = "1" ] && exit 0

[ "${HERDR_ENV:-}" = "1" ] || exit 0
[ -n "${HERDR_PANE_ID:-}" ] || exit 0
command -v herdr >/dev/null 2>&1 || exit 0
command -v jq >/dev/null 2>&1 || exit 0
command -v claude >/dev/null 2>&1 || exit 0
command -v timeout >/dev/null 2>&1 || exit 0

# Read the hook payload: the just-submitted prompt (required, the topic signal)
# and the transcript path (optional, prior context).
input="$(cat)"
prompt="$(printf '%s' "$input" | jq -r '.prompt // empty')"
[ -n "$prompt" ] || exit 0
transcript="$(printf '%s' "$input" | jq -r '.transcript_path // empty')"

# Resolve the workspace (required) and tab (optional) from the pane.
pane_json="$(herdr pane get "$HERDR_PANE_ID" 2>/dev/null)"
workspace_id="$(printf '%s' "$pane_json" | jq -r '.result.pane.workspace_id // empty')"
tab_id="$(printf '%s' "$pane_json" | jq -r '.result.pane.tab_id // empty')"
[ -n "$workspace_id" ] || exit 0
label="$(herdr workspace get "$workspace_id" 2>/dev/null | jq -r '.result.workspace.label // empty')"

# Decide whether the user named this workspace, before spending a summarizer
# call. With a marker, any other label means a manual rename. Without one, the
# hook has never named it, so fall back to herdr's persisted state: a non-null
# custom_name there is a name we did not give. When that state cannot be read
# (file missing, format changed), we cannot tell, so go ahead and name it.
session="${HERDR_SESSION:-default}"
state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/herdr-workspace-name/${session}"
marker="${state_dir}/${workspace_id}"
if [ -f "$marker" ]; then
  [ "$label" = "$(cat "$marker" 2>/dev/null)" ] || exit 0
else
  if [ "$session" = "default" ]; then
    herdr_state="$HOME/.config/herdr/session.json"
  else
    herdr_state="$HOME/.config/herdr/sessions/${session}/session.json"
  fi
  if [ -f "$herdr_state" ]; then
    custom_name="$(jq -r --arg id "$workspace_id" \
      '.workspaces[]? | select(.id == $id) | .custom_name // empty' \
      "$herdr_state" 2>/dev/null)"
    [ -z "$custom_name" ] || exit 0
  fi
fi

# Keep the summarizer cheap even when the prompt is long.
prompt="$(printf '%s' "$prompt" | cut -c1-600)"

# Collapse transcript entries into "role: text" lines, one message per line.
# Shared by the opening request and the recent context below.
collapse='
  [ .[]
    | select((.message | type) == "object")
    | select((.type == "user" and (.message.content | type == "string"))
             or (.type == "assistant" and (.message.content | type == "array")))
    | {
        role: .message.role,
        text: (
          if (.message.content | type == "string") then .message.content
          else (.message.content | map(select(.type == "text") | .text) | join(" ")) end
        ),
      }
    | select(.text | length > 0)
    | select(.text | startswith("<") | not)
    | .role + ": " + ((.text | gsub("\\s+"; " "))[0:500])
  ]'

# Recover the session's theme cheaply instead of reading the whole transcript:
# the opening request (the first user message, from the head of the file) plus
# the last few messages. A missing or unreadable transcript just means "no extra
# context". Bound the input with head/tail: 80 raw lines comfortably cover 8
# messages once non-message events are filtered out.
opening=""
context=""
if [ -n "$transcript" ] && [ -f "$transcript" ]; then
  opening="$(head -n 200 "$transcript" 2>/dev/null \
    | jq -s -r "${collapse} | map(select(startswith(\"user: \"))) | .[0] // empty" 2>/dev/null)"
  context="$(tail -n 80 "$transcript" 2>/dev/null \
    | jq -s -r "${collapse} | .[-8:] | .[]" 2>/dev/null)"
fi

# The current label is the session's theme so far. Older labels may carry a
# legacy "branch: " prefix; strip it to compare themes, not prefixes.
case "$label" in
  *": "*) topic_current="${label#*: }" ;;
  *)      topic_current="$label" ;;
esac

instruction="Current title: \"${topic_current}\"
New request: \"${prompt}\"

<opening>
${opening}
</opening>

<recent>
${context}
</recent>

Title the theme this whole session is working on. <opening> is the request that
started the session; <recent> is the latest conversation. Output exactly one
line, nothing else:
- If the new request continues the session's theme (details, fixes, or checks
  on the same theme), output only:
  KEEP
- Otherwise (the theme changed, or the current title is a placeholder such as a
  number or a directory name) output a single emoji that fits the theme, then
  one half-width space, then the title. Write the title in Japanese: a noun
  phrase of at most 20 characters, with no punctuation, no quotes, and no
  trailing symbol. Keep proper nouns and command names as written.
  Example: 🐛 ログイン時のクラッシュ修正"

# Isolate the summarizer from the herdr integration: unset the herdr env so the
# sibling agent-state hook cannot remap this pane, and set the recursion guard so
# this hook no-ops in the child. Bound it with a timeout.
summary="$(env -u HERDR_ENV -u HERDR_PANE_ID -u HERDR_SOCKET_PATH HERDR_RENAME=1 \
  timeout 30 claude --print --model haiku "$instruction" </dev/null 2>/dev/null \
  | head -n1 | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
[ -n "$summary" ] || exit 0

# KEEP means the theme is unchanged — nothing to do, and no label churn. The
# summarizer does not always emit the bare token: it may wrap it (e.g. "🔒 KEEP",
# "\"KEEP\"", or "KEEP.") while still meaning "keep". Strip any leading run of
# non-letters (emoji, quotes, spaces) and trailing non-letters, then compare
# case-insensitively so those variants no longer leak through as a "KEEP" label.
core="$(printf '%s' "$summary" | sed 's/^[^[:alpha:]]*//; s/[^[:alpha:]]*$//')"
case "$core" in
  [Kk][Ee][Ee][Pp]) exit 0 ;;
esac

# Validate the shape before trusting it as a label: require two space-separated
# tokens (the intended "<emoji> <title>") and reject preambles, refusals, or full
# sentences rather than renaming to garbage.
case "$summary" in
  *" "*) : ;;
  *) exit 0 ;;
esac
printf '%s' "$summary" | grep -Eq '[.?!。？！]|^(I |Sorry|Here|Sure|The )|(以下|タイトル|申し訳)' && exit 0

# Cap the length by characters, not bytes: the title is Japanese, so a byte cut
# would split a multibyte character. jq slices strings by code point.
topic="$(printf '%s' "$summary" | jq -Rr '.[0:32]')"
[ -n "$topic" ] || exit 0

herdr workspace rename "$workspace_id" "$topic" >/dev/null 2>&1 || exit 0
mkdir -p "$state_dir" 2>/dev/null && printf '%s' "$topic" > "$marker"
[ -n "$tab_id" ] && herdr tab rename "$tab_id" "$topic" >/dev/null 2>&1 || true
exit 0
