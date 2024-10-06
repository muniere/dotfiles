import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec, TmplSpec } from "../../lib/schema.ts";

export const ZshCookBook = new CookBook({
  name: "ZshCookBook",
  prefs: [
    new PrefSpec({
      src: "zsh/",
      dst: HomeLayout.config().join("zsh/"),
    }, {
      layout: "by-component",
    }),
  ],
  tmpls: [
    new TmplSpec({
      src: "zshenv",
      dst: "~/.zshenv",
    }, {
      values: {
        cache: HomeLayout.cache().transHome(),
        config: HomeLayout.config().transHome(),
        data: HomeLayout.data().transHome(),
        state: HomeLayout.state().transHome(),
        runtime: HomeLayout.runtime().transHome(),
      },
    }),
  ],
  container: ResLayout.vault(),
});
