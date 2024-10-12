import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const AsdfCookBook = new CookBook({
  name: "AsdfCookBook",
  container: ResLayout.vault().join("asdf/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("asdf/"),
    }),
  ],
});
