#!/usr/bin/env bash
# Name this herdr workspace and tab in Japanese after what the session works on.
# Custom hook, installed beside the herdr-managed herdr-agent-state.sh. Wired as a
# global UserPromptSubmit hook (async). Best-effort:
# silently no-ops whenever anything is missing or we are not inside herdr.
#
# The two names differ in scope:
# - The tab names the task its session is on right now ("ログイン時のクラッシュ修正").
#   It follows the conversation: opening request, recent messages, new prompt.
# - The workspace names the broad goal its tabs serve ("🔐 認証まわりの改善"). It
#   is revisited only when a tab's task changes, and only from the tabs' titles
#   and memos, so a passing remark in one session does not rename it.
#
# Both names, plus a short memo of each theme, persist in a per-workspace state
# file. The memos carry the theme across a long session, after its opening
# request has scrolled out of the recent messages.
#
# IDs are not part of any name: the herdr plugin workspace-meta reports them,
# with the tab labels, for the sidebar to show.
#
# A name the user gave by hand is never overwritten. herdr does not record who
# set a label (its custom_name is filled by API renames too), so the state file
# keeps each label with its trigger: `auto` for one this hook set, `manual` for
# one set by hand. A label that differs from the stored one was set by hand
# since, and is stored as `manual`; its memo stays up to date, but the name is
# left alone. Renaming it to `auto` hands it back to this hook, which names it
# afresh on the next prompt (herdr has no way to clear a name).

# The summarizer below spawns `claude -p`, whose own prompt would fire this hook
# again. The child runs with HERDR_RENAME=1 (set below), so any nested invocation
# returns at once.
[ "${HERDR_RENAME:-}" = "1" ] && exit 0

[ "${HERDR_ENV:-}" = "1" ] || exit 0
[ -n "${HERDR_PANE_ID:-}" ] || exit 0
command -v herdr >/dev/null 2>&1 || exit 0
command -v jq >/dev/null 2>&1 || exit 0

# Read the hook payload: the just-submitted prompt (the topic signal), the
# transcript path (prior context), and the session ID.
input="$(cat)"
prompt="$(printf '%s' "$input" | jq -r '.prompt // empty')"
[ -n "$prompt" ] || exit 0
transcript="$(printf '%s' "$input" | jq -r '.transcript_path // empty')"
session_id="$(printf '%s' "$input" | jq -r '.session_id // empty')"

# Resolve the workspace (required) and tab (optional) from the pane.
pane_json="$(herdr pane get "$HERDR_PANE_ID" 2>/dev/null)"
workspace_id="$(printf '%s' "$pane_json" | jq -r '.result.pane.workspace_id // empty')"
tab_id="$(printf '%s' "$pane_json" | jq -r '.result.pane.tab_id // empty')"
[ -n "$workspace_id" ] || exit 0

command -v claude >/dev/null 2>&1 || exit 0
command -v timeout >/dev/null 2>&1 || exit 0

ws_label="$(herdr workspace get "$workspace_id" 2>/dev/null | jq -r '.result.workspace.label // empty')"
tab_label=""
tab_number=""
if [ -n "$tab_id" ]; then
  tab_json="$(herdr tab get "$tab_id" 2>/dev/null)"
  tab_label="$(printf '%s' "$tab_json" | jq -r '.result.tab.label // empty')"
  tab_number="$(printf '%s' "$tab_json" | jq -r '.result.tab.number // empty')"
fi

# Load the state file: {workspace: {label, trigger, memo}, tabs: {<tab_id>:
# {label, trigger, memo, session_id}}}. A missing or broken file is an empty
# state.
session="${HERDR_SESSION:-default}"
state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/herdr-workspace-name/${session}"
state_file="${state_dir}/${workspace_id}.json"
state="$(jq -c 'select(type == "object")' "$state_file" 2>/dev/null)"
[ -n "$state" ] || state='{}'
ws_stored="$(printf '%s' "$state" | jq -r '.workspace.label // empty')"
ws_stored_trigger="$(printf '%s' "$state" | jq -r '.workspace.trigger // empty')"
ws_memo="$(printf '%s' "$state" | jq -r '.workspace.memo // empty')"
tab_stored="$(printf '%s' "$state" | jq -r --arg t "$tab_id" '.tabs[$t].label // empty')"
tab_stored_trigger="$(printf '%s' "$state" | jq -r --arg t "$tab_id" '.tabs[$t].trigger // empty')"
tab_memo="$(printf '%s' "$state" | jq -r --arg t "$tab_id" '.tabs[$t].memo // empty')"

# Older versions of this hook kept only a plain-text marker: the one label they
# set on both the workspace and the tab.
legacy_marker="${state_dir}/${workspace_id}"
legacy="$(cat "$legacy_marker" 2>/dev/null)"

# Without a stored label, fall back to herdr's persisted state: a non-null
# custom_name there is a name we did not give. When that state cannot be read
# (file missing, format changed), we cannot tell, so go ahead and name it.
if [ "$session" = "default" ]; then
  herdr_state="$HOME/.config/herdr/session.json"
else
  herdr_state="$HOME/.config/herdr/sessions/${session}/session.json"
fi
ws_custom=""
tab_custom=""
if [ -f "$herdr_state" ]; then
  ws_custom="$(jq -r --arg id "$workspace_id" \
    '.workspaces[]? | select(.id == $id) | .custom_name // empty' \
    "$herdr_state" 2>/dev/null)"
  # Tabs carry no ID there; they are listed in order, matching the tab number.
  if [ -n "$tab_number" ]; then
    tab_custom="$(jq -r --arg id "$workspace_id" --argjson n "$tab_number" \
      '.workspaces[]? | select(.id == $id) | .tabs[$n - 1]?.custom_name // empty' \
      "$herdr_state" 2>/dev/null)"
  fi
fi

# trigger_of <current label> <stored label> <stored trigger> <herdr custom_name>:
# who set the current label, before spending a summarizer call. Prints `reset`
# for the `auto` label that hands a name back, else `auto` or `manual`. Entries
# from before triggers were stored are all `auto`.
trigger_of() {
  if [ "$1" = "auto" ]; then
    echo reset
  elif [ -n "$2" ]; then
    if [ "$1" = "$2" ]; then echo "${3:-auto}"; else echo manual; fi
  elif [ -n "$legacy" ]; then
    if [ "$1" = "$legacy" ]; then echo auto; else echo manual; fi
  elif [ -z "$4" ]; then
    echo auto
  else
    echo manual
  fi
}

# Resolve each trigger and the name to show the summarizer: ours for `auto`
# (empty when there is none yet, so it gets one), the user's for `manual`.
ws_trigger="$(trigger_of "$ws_label" "$ws_stored" "$ws_stored_trigger" "$ws_custom")"
case "$ws_trigger" in
  reset)  ws_trigger=auto; ws_name="" ;;
  auto)   ws_name="$ws_stored" ;;
  manual) ws_name="$ws_label" ;;
esac
tab_trigger=""
tab_name=""
if [ -n "$tab_id" ]; then
  tab_trigger="$(trigger_of "$tab_label" "$tab_stored" "$tab_stored_trigger" "$tab_custom")"
  case "$tab_trigger" in
    reset)  tab_trigger=auto; tab_name="" ;;
    auto)   tab_name="$tab_stored" ;;
    manual) tab_name="$tab_label" ;;
  esac
fi

# Without a tab there is nothing to follow; the workspace still needs a first
# name.
[ -n "$tab_id" ] || { [ "$ws_trigger" = auto ] && [ -z "$ws_name" ]; } || exit 0

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
# context". Bound the input with head/tail: 80 raw lines comfortably cover 6
# messages once non-message events are filtered out.
opening=""
context=""
if [ -n "$transcript" ] && [ -f "$transcript" ]; then
  opening="$(head -n 200 "$transcript" 2>/dev/null \
    | jq -s -r "${collapse} | map(select(startswith(\"user: \"))) | .[0] // empty" 2>/dev/null)"
  context="$(tail -n 80 "$transcript" 2>/dev/null \
    | jq -s -r "${collapse} | .[-6:] | .[]" 2>/dev/null)"
fi

# summarize <instruction>: ask the summarizer for one JSON object and print it
# compactly, or nothing when the reply holds no object. Isolate the summarizer
# from the herdr integration: unset the herdr env so the sibling agent-state
# hook cannot remap this pane, and set the recursion guard so this hook no-ops
# in the child. Bound it with a timeout; two calls must fit the hook's timeout.
# `claude -p` occasionally exits at once with no output; retry that case once.
summarize() {
  local reply started="$SECONDS"
  reply="$(summarize_once "$1")"
  if [ -z "$reply" ] && [ $((SECONDS - started)) -lt 5 ]; then
    reply="$(summarize_once "$1")"
  fi
  printf '%s' "$reply"
}
summarize_once() {
  env -u HERDR_ENV -u HERDR_PANE_ID -u HERDR_SOCKET_PATH HERDR_RENAME=1 \
    timeout 25 claude --print --model haiku "$1" </dev/null 2>/dev/null \
    | tr '\n\r' '  ' \
    | sed -n 's/^[^{]*\({.*}\)[^}]*$/\1/p' \
    | jq -c 'select(type == "object")' 2>/dev/null
}

# title_of <reply> <max chars>: the reply's title when it names a new one, or
# nothing for KEEP and for anything that does not look like a title.
title_of() {
  local title core
  title="$(printf '%s' "$1" | jq -r '.title // empty | tostring' \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  [ -n "$title" ] || return 0
  # The summarizer may wrap KEEP (e.g. "🔒 KEEP", "\"KEEP\"", or "KEEP."). Strip
  # leading and trailing non-letters, then compare case-insensitively.
  core="$(printf '%s' "$title" | sed 's/^[^[:alpha:]]*//; s/[^[:alpha:]]*$//')"
  case "$core" in
    [Kk][Ee][Ee][Pp]) return 0 ;;
  esac
  # Reject preambles, refusals, or full sentences rather than renaming to garbage.
  printf '%s' "$title" | grep -Eq '[.?!。？！]|^(I |Sorry|Here|Sure|The )|(以下|タイトル|申し訳)' && return 0
  # Cap the length by characters, not bytes: the title is Japanese, so a byte cut
  # would split a multibyte character. jq slices strings by code point.
  printf '%s' "$title" | jq -Rr --argjson n "$2" '.[0:$n]'
}

# memo_of <reply> <fallback>: the reply's memo, or the fallback when it has none.
memo_of() {
  local memo
  memo="$(printf '%s' "$1" | jq -r '.memo // empty | tostring | gsub("\\s+"; " ") | .[0:160]')"
  printf '%s' "${memo:-$2}"
}

# --- Tab: the task this session is on right now ---------------------------

tab_entry='null'
tab_changed=0
if [ -n "$tab_id" ]; then
  instruction="<workspace>
Title: ${ws_name:-(none)}
Memo: ${ws_memo:-(none)}
</workspace>

<tab>
Title: ${tab_name:-(none)}
Memo: ${tab_memo:-(none)}
</tab>

<opening>
${opening}
</opening>

<recent>
${context}
</recent>

<new>
${prompt}
</new>

The tab above hosts one coding session inside the workspace above. <opening> is
the request that started the session, <recent> the latest conversation, and
<new> the request just submitted. Output exactly one JSON object on one line,
nothing else:
{\"title\": \"...\", \"memo\": \"...\"}
- title: if the tab has a title and the new request continues its task
  (details, fixes, or checks on the same task), output \"KEEP\". Otherwise a
  title for the task the session is on now: a Japanese noun phrase of at most
  20 characters, more specific than the workspace title, with no emoji, no
  punctuation, no quotes, and no trailing symbol. Keep proper nouns and command
  names as written. Example: ログイン時のクラッシュ修正
- memo: one or two Japanese sentences, at most 120 characters, on what the
  session is trying to achieve and where it stands. Start from the tab's memo
  and change only what the session has moved past."
  reply="$(summarize "$instruction")"
  memo="$(memo_of "$reply" "$tab_memo")"
  if [ "$tab_trigger" = manual ]; then
    # Keep the user's name; record it, with the fresh memo.
    tab_entry="$(jq -nc --arg l "$tab_label" --arg m "$memo" --arg s "$session_id" \
      '{label: $l, trigger: "manual", memo: $m, session_id: $s}')"
  else
    new_title=""
    [ -n "$reply" ] && new_title="$(title_of "$reply" 24)"
    tab_final="$tab_name"
    if [ -n "$new_title" ] && [ "$new_title" != "$tab_label" ] \
      && herdr tab rename "$tab_id" "$new_title" >/dev/null 2>&1; then
      tab_final="$new_title"
      tab_changed=1
    fi
    # Without a title of ours yet (KEEP or a rejected reply on first naming),
    # store nothing: the current label is a placeholder, or `auto`.
    if [ -n "$tab_final" ]; then
      tab_entry="$(jq -nc --arg l "$tab_final" --arg m "$memo" --arg s "$session_id" \
        '{label: $l, trigger: "auto", memo: $m, session_id: $s}')"
    fi
  fi
fi

# --- Workspace: the broad goal its tabs serve ------------------------------

ws_entry='null'
# Emoji the workspace title may start with. Each has Emoji_Presentation=Yes, so
# herdr and the terminal agree it is two cells wide; a text-default one such as
# 🏷 is counted as one cell but drawn as two, hiding the space after it.
ws_emojis="🔧 🐛 ✨ 📝 🚀 🔍 🎨 📦 🧪 🔐 ⚡ 📊 🧹 🔀 🌐 📚 🤖 💡 🔥 📁 📐 🧩 💬 🎯 🔌 🧭 💻 🚧"
live_tabs="$(herdr tab list 2>/dev/null \
  | jq -c --arg w "$workspace_id" '[.result.tabs[]? | select(.workspace_id == $w) | {id: .tab_id, label}]' 2>/dev/null)"
[ -n "$live_tabs" ] || live_tabs='[]'
# A manual name is not reviewed, but its memo is, on the same occasions.
if { [ "$ws_trigger" = auto ] && [ -z "$ws_name" ]; } || [ "$tab_changed" = 1 ]; then
  # List every tab by its live label (manual names included) and stored memo,
  # with this tab's fresh entry taking precedence over the state read above.
  tabs="$(printf '%s' "$state" | jq -r \
    --argjson live "$live_tabs" --arg t "$tab_id" --argjson mine "$tab_entry" '
      (.tabs // {}) as $s
      | ($live | if length == 0 then [{id: $t, label: ""}] else . end)
      | map(
          (if .id == $t and $mine then $mine else ($s[.id] // {}) end) as $e
          | "- " + ((if .id == $t and $mine then $e.label else .label end) // "")
            + " — " + ($e.memo // ""))
      | .[]' 2>/dev/null)"
  instruction="<workspace>
Title: ${ws_name:-(none)}
Memo: ${ws_memo:-(none)}
</workspace>

<tabs>
${tabs}
</tabs>

<opening>
${opening}
</opening>

A workspace groups the tabs above, each a coding session (title — memo).
<opening> is the request that started one of them. Name the broad goal the
workspace serves: wider than any single tab's task, so the name stays valid as
tasks come and go. Output exactly one JSON object on one line, nothing else:
{\"title\": \"...\", \"memo\": \"...\"}
- title: if the workspace has a title that still covers every tab, output
  \"KEEP\". Otherwise (no title yet, or the tabs have moved to another goal) a
  single emoji that fits the goal, chosen from this list only:
  ${ws_emojis}
  then one half-width space, then a Japanese noun phrase of at most 16
  characters, with no punctuation, no quotes, and no trailing symbol. Keep
  proper nouns and command names as written.
  Example: 🔐 認証まわりの改善
- memo: one or two Japanese sentences, at most 120 characters, on the goal the
  workspace serves. Keep the workspace's memo unless the goal changed."
  reply="$(summarize "$instruction")"
  ws_memo="$(memo_of "$reply" "$ws_memo")"
  if [ -n "$reply" ] && [ "$ws_trigger" = auto ]; then
    new_title="$(title_of "$reply" 28)"
    # Require the "<emoji> <title>" shape, and an emoji from the list: drop a
    # variation selector (U+FE0F) and replace anything else with the first one.
    case "$new_title" in
      *" "*)
        emoji="${new_title%% *}"
        emoji="${emoji//$(printf '\357\270\217')/}"
        case " ${ws_emojis} " in
          *" ${emoji} "*) : ;;
          *) emoji="${ws_emojis%% *}" ;;
        esac
        new_title="${emoji} ${new_title#* }"
        ;;
      *) new_title="" ;;
    esac
    ws_final="$ws_name"
    if [ -n "$new_title" ] && [ "$new_title" != "$ws_label" ] \
      && herdr workspace rename "$workspace_id" "$new_title" >/dev/null 2>&1; then
      ws_final="$new_title"
    fi
    if [ -n "$ws_final" ]; then
      ws_entry="$(jq -nc --arg l "$ws_final" --arg m "$ws_memo" \
        '{label: $l, trigger: "auto", memo: $m}')"
    fi
  fi
fi
# Record a manual name whether or not it was reviewed, so the trigger sticks.
if [ "$ws_trigger" = manual ]; then
  ws_entry="$(jq -nc --arg l "$ws_label" --arg m "$ws_memo" \
    '{label: $l, trigger: "manual", memo: $m}')"
fi

# --- Persist ---------------------------------------------------------------

[ "$tab_entry" != 'null' ] || [ "$ws_entry" != 'null' ] || exit 0
mkdir -p "$state_dir" 2>/dev/null || exit 0

# Tabs of one workspace run this hook concurrently, so re-read the state under a
# lock and patch only what this run decided. A lock left by a killed run is
# taken over after a few seconds rather than blocking every later run. Release
# only a lock this run took, so a run that gave up waiting does not drop another's.
lock="${state_file}.lock"
locked=0
for _ in $(seq 30); do
  mkdir "$lock" 2>/dev/null && locked=1 && break
  sleep 0.1
done
trap '[ "$locked" = 1 ] && rmdir "$lock" 2>/dev/null' EXIT

current="$(jq -c 'select(type == "object")' "$state_file" 2>/dev/null)"
[ -n "$current" ] || current='{}'
# Drop tabs that were closed, unless the tab list could not be read.
printf '%s' "$current" | jq \
  --arg t "$tab_id" --argjson tab "$tab_entry" --argjson ws "$ws_entry" \
  --argjson live "$(printf '%s' "$live_tabs" | jq -c 'map(.id)')" '
    (if $tab then .tabs[$t] = $tab else . end)
    | (if $ws then .workspace = $ws else . end)
    | if ($live | length) > 0
      then .tabs = ((.tabs // {}) | with_entries(select(.key as $k | $live | index($k))))
      else . end' > "${state_file}.tmp" 2>/dev/null \
  && mv "${state_file}.tmp" "$state_file" || exit 0
# The legacy marker vouches for the workspace label until the state holds one.
jq -e '.workspace.label' "$state_file" >/dev/null 2>&1 && rm -f "$legacy_marker"
exit 0
