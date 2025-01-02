import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const BatCookBook = new CookBook({
  name: "BatCookBook",
  container: ResLayout.vault().join("bat/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("bat/"),
    }),
  ],
});
