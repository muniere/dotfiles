import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const TmuxCookBook = new CookBook({
  name: "TmuxCookBook",
  container: ResLayout.vault().join("tmux/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("tmux/"),
    }),
  ],
});
