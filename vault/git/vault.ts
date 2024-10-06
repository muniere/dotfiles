import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const GitCookBook = new CookBook({
  name: "GitCookBook",
  prefs: [
    new PrefSpec({
      src: "git/",
      dst: HomeLayout.config().join("git/"),
    }, {
      layout: "by-component",
    }),
  ],
  container: ResLayout.vault(),
});
