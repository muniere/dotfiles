import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const VifmCookBook = new CookBook({
  name: "VifmCookBook",
  container: ResLayout.vault().join("vifm/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("vifm/"),
    }),
  ],
});
