import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const ShCookBook = new CookBook({
  name: "ShCookBook",
  prefs: [
    new PrefSpec({
      src: "sh/",
      dst: HomeLayout.config().join("sh/"),
    }, {
      layout: "by-component",
    }),
  ],
  container: ResLayout.vault(),
});
