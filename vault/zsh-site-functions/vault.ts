import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

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
