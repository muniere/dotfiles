import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const ClaudeCookBook = new CookBook({
  name: "ClaudeCookBook",
  container: ResLayout.vault().join("claude/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.bin(),
    }),
  ],
});
