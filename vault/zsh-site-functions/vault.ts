import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const ZshSiteFunctionsCookBook = new CookBook({
  name: "ZshSiteFunctionsCookBook",
  container: ResLayout.vault().join("zsh-site-functions/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.data().join("zsh/site-functions/"),
    }),
  ],
});
