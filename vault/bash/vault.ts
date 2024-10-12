import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec, TmplSpec } from "@dotfiles/lib/schema.ts";

export const BashCookBook = new CookBook({
  name: "BashCookBook",
  container: ResLayout.vault().join("bash/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("bash/"),
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
});
