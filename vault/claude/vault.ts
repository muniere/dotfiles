import { ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import { Path } from "@dotfiles/lib/path.ts";

export const ClaudeCookBook = new CookBook({
  name: "ClaudeCookBook",
  container: ResLayout.vault().join("claude/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: new Path("~/.claude").expandHome(),
    }),
  ],
});
