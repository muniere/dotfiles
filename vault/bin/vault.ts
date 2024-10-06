import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

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
