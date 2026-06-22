import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const ZellijCookBook = new CookBook({
  name: "ZellijCookBook",
  container: ResLayout.vault().join("zellij/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("zellij/"),
    }),
  ],
});
