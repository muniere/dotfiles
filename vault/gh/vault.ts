import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const GitHubCookBook = new CookBook({
  name: "GitHubCookBook",
  container: ResLayout.vault().join("gh/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.data().join("gh/"),
    }),
  ],
});
