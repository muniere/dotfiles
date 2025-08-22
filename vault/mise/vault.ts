import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { Path } from "@dotfiles/lib/path.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const MiseCookBook = new CookBook({
  name: "MiseCookBook",
  container: ResLayout.vault().join("mise/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("mise/"),
    }),
  ],
});

export const MiseCompletionCookBook = new CookBook({
  name: "MiseCompletionCookBook",
  container: ResLayout.vault().join("mise/"),
  prefs: [
    new PrefSpec({
      src: new Path("/opt/homebrew/etc/bash_completion.d/mise"),
      dst: HomeLayout.data().join("bash/bash_completion.d/mise"),
    }),
    new PrefSpec({
      src: new Path("/opt/homebrew/share/zsh/site-functions/_mise"),
      dst: HomeLayout.data().join("zsh/site-functions/_mise"),
    }),
  ],
  platforms: ["darwin"],
});
