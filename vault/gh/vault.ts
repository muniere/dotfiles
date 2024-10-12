import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

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
