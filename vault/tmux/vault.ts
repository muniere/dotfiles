import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const TmuxCookBook = new CookBook({
  name: "TmuxCookBook",
  prefs: [
    new PrefSpec({
      src: "tmux/",
      dst: HomeLayout.config().join("tmux/"),
    }, {
      layout: "by-component",
    }),
  ],
  container: ResLayout.vault(),
});
