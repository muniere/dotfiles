#!/usr/bin/env bash
# Rename this herdr workspace (and tab) to the work in progress *right now*.
# Custom hook, installed beside the herdr-managed herdr-agent-state.sh. Wired as a
# global UserPromptSubmit hook (async): it fires the instant a prompt is
# submitted, so the label names what is being worked on now — not a summary of
# what has already finished. It reads the new prompt from the hook payload (the
# primary topic signal) plus the recent transcript (for the context a bare prompt
# lacks), summarizes them into a short "<emoji> label", and renames the workspace
# (and tab) only when the topic actually changed. Best-effort: silently no-ops
# whenever anything is missing or we are not inside herdr.

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

# Keep the summarizer cheap even when the prompt is long.
prompt="$(printf '%s' "$prompt" | cut -c1-600)"

# Recover recent context: the last few conversation messages, each collapsed to
# one line and capped, so the summarizer sees more than the bare prompt. The new
# prompt is passed separately above, so a missing or unreadable transcript just
# means "no extra context" rather than a failure. Bound the input with `tail`: we
# only keep the last 8 messages, so slurping the whole session is wasteful — 80
# raw lines comfortably cover 8 messages once non-message events are filtered out.
context=""
if [ -n "$transcript" ] && [ -f "$transcript" ]; then
  context="$(tail -n 80 "$transcript" 2>/dev/null | jq -s -r '
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
      | select((.text | startswith("<local-command")) or (.text | startswith("<command-")) | not)
      | .role + ": " + ((.text | gsub("\\s+"; " "))[0:500])
    ] | .[-8:] | .[]
  ' 2>/dev/null)"
fi

# Resolve the workspace (required) and tab (optional) from the pane.
pane_json="$(herdr pane get "$HERDR_PANE_ID" 2>/dev/null)"
workspace_id="$(printf '%s' "$pane_json" | jq -r '.result.pane.workspace_id // empty')"
tab_id="$(printf '%s' "$pane_json" | jq -r '.result.pane.tab_id // empty')"
[ -n "$workspace_id" ] || exit 0

# Recover the current work topic from the existing label so the summarizer can
# leave it untouched when the new request stays on the same topic. Older labels
# may carry a legacy "branch: " prefix; strip it to compare topics, not prefixes.
label="$(herdr workspace get "$workspace_id" 2>/dev/null | jq -r '.result.workspace.label // empty')"
case "$label" in
  *": "*) topic_current="${label#*: }" ;;
  *)      topic_current="$label" ;;
esac

instruction="Current work topic: \"${topic_current}\"
New request: \"${prompt}\"

<conversation>
${context}
</conversation>

Name what is being worked on right now. Output exactly one line, nothing else:
- If the new request continues the same topic as the current work, output only:
  KEEP
- Otherwise (a different topic, or the current work is just a placeholder number
  or name) output a single emoji that fits the topic, then one space, then a
  short label of at most 5 words. No quotes, no punctuation, no trailing period.
  Write the label in English even if the request is in another language.
  Example: 🐛 fix login crash"

# Isolate the summarizer from the herdr integration: unset the herdr env so the
# sibling agent-state hook cannot remap this pane, and set the recursion guard so
# this hook no-ops in the child. Bound it with a timeout.
summary="$(env -u HERDR_ENV -u HERDR_PANE_ID -u HERDR_SOCKET_PATH HERDR_RENAME=1 \
  timeout 30 claude -p "$instruction" </dev/null 2>/dev/null \
  | head -n1 | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
[ -n "$summary" ] || exit 0

# KEEP means the topic is unchanged — nothing to do, and no label churn. The
# summarizer does not always emit the bare token: it may wrap it (e.g. "🔒 KEEP",
# "\"KEEP\"", or "KEEP.") while still meaning "keep". Strip any leading run of
# non-letters (emoji, quotes, spaces) and trailing non-letters, then compare
# case-insensitively so those variants no longer leak through as a "KEEP" label.
core="$(printf '%s' "$summary" | sed 's/^[^[:alpha:]]*//; s/[^[:alpha:]]*$//')"
case "$core" in
  [Kk][Ee][Ee][Pp]) exit 0 ;;
esac

# Validate the shape before trusting it as a label: require two space-separated
# tokens (the intended "<emoji> <words>") and reject preambles, refusals, or full
# sentences rather than renaming to garbage.
case "$summary" in
  *" "*) : ;;
  *) exit 0 ;;
esac
printf '%s' "$summary" | grep -Eq '[.?!]|^(I |Sorry|Here|Sure|The )' && exit 0

# Cap the length; the label is requested in English (ASCII) after a leading emoji,
# so under that expectation a byte cut at column 40 lands well past the emoji and
# cannot split a multibyte character.
topic="$(printf '%s' "$summary" | cut -c1-40)"
[ -n "$topic" ] || exit 0

herdr workspace rename "$workspace_id" "$topic" >/dev/null 2>&1 || true
[ -n "$tab_id" ] && herdr tab rename "$tab_id" "$topic" >/dev/null 2>&1 || true
exit 0
