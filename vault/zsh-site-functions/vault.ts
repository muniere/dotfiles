import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const ZshSiteFunctionsCookBook = new CookBook({
  name: "ZshSiteFunctionsCookBook",
  prefs: [
    new PrefSpec({
      src: "zsh-site-functions/",
      dst: HomeLayout.data().join("zsh/site-functions/"),
    }, {
      layout: "by-component",
    }),
  ],
  container: ResLayout.vault(),
});
