import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const GitHubCookBook = new CookBook({
  name: "GitHubCookBook",
  prefs: [
    new PrefSpec({
      src: "gh/",
      dst: HomeLayout.data().join("gh/"),
    }, {
      layout: "by-component",
    }),
  ],
  container: ResLayout.vault(),
});
