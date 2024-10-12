import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

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
