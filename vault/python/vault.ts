import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const PythonCookBook = new CookBook({
  name: "PythonCookBook",
  prefs: [
    new PrefSpec({
      src: "python/",
      dst: HomeLayout.config().join("python/"),
    }, {
      layout: "by-component",
    }),
  ],
  container: ResLayout.vault(),
});
