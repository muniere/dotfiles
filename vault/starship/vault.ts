import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const StarshipCookBook = new CookBook({
  name: "StarshipCookBook",
  container: ResLayout.vault().join("starship/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("starship/"),
    }),
  ],
});
