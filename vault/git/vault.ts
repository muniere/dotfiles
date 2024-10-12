import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const GitCookBook = new CookBook({
  name: "GitCookBook",
  container: ResLayout.vault().join("git/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("git/"),
    }),
  ],
});
