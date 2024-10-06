import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec, TmplSpec } from "../../lib/schema.ts";

export const BashCookBook = new CookBook({
  name: "BashCookBook",
  prefs: [
    new PrefSpec({
      src: "bash/",
      dst: HomeLayout.config().join("bash/"),
    }, {
      layout: "by-component",
    }),
  ],
  tmpls: [
    new TmplSpec({
      src: "bashrc",
      dst: "~/.bashrc",
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
