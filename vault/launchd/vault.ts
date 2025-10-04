import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const LaunchdCookBook = new CookBook({
  name: "LaunchdCookBook",
  container: ResLayout.vault().join("launchd/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.data().join("zsh/site-functions/"),
    }),
  ],
});
