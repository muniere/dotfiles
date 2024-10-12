import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const BinCookBook = new CookBook({
  name: "BinCookBook",
  container: ResLayout.vault().join("bin/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.bin(),
    }),
  ],
});
