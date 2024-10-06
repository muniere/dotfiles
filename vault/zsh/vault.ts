import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec, TmplSpec } from "../../lib/schema.ts";

export const ZshCookBook = new CookBook({
  name: "ZshCookBook",
  container: ResLayout.vault().join("zsh/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("zsh/"),
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
});
