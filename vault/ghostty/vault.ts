import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const GhosttyCookBook = new CookBook({
  name: "GhosttyCookBook",
  container: ResLayout.vault().join("ghostty/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("ghostty/"),
    }),
  ]
});
