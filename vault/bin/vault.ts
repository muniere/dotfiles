import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const BinCookBook = new CookBook({
  name: "BinCookBook",
  prefs: [
    new PrefSpec({
      src: "bin/",
      dst: HomeLayout.bin(),
    }, {
      layout: "by-component",
    }),
  ],
  container: ResLayout.vault(),
});
