// hunk: review-first terminal diff viewer for agent-authored changesets.
// Reference: https://hunk.dev/
import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const HunkCookBook = new CookBook({
  name: "HunkCookBook",
  container: ResLayout.vault().join("hunk/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("hunk/"),
    }),
  ],
});
