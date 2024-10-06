import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const ShCookBook = new CookBook({
  name: "ShCookBook",
  container: ResLayout.vault().join("sh/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("sh/"),
    }),
  ],
});
