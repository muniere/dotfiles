import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const MiseCookBook = new CookBook({
  name: "MiseCookBook",
  container: ResLayout.vault().join("mise/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("mise/"),
    }),
  ],
});
