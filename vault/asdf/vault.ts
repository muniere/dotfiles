import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const AsdfCookBook = new CookBook({
  name: "AsdfCookBook",
  prefs: [
    new PrefSpec({
      src: "asdf/",
      dst: HomeLayout.config().join("asdf/"),
    }, {
      layout: "by-component",
    }),
  ],
  container: ResLayout.vault(),
});
