import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const GitGtrCookBook = new CookBook({
  name: "GitGtrCookBook",
  container: ResLayout.vault().join("git-gtr/"),
  prefs: [
    new PrefSpec({
      src: "./site-functions/_git_gtr",
      dst: HomeLayout.data().join("zsh/site-functions/_git_gtr"),
    }),
    new PrefSpec({
      src: "./site-functions/_gtr",
      dst: HomeLayout.data().join("zsh/site-functions/_gtr"),
    }),
  ],
  platforms: ["darwin"],
});
