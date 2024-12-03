import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const SqlfluffCookBook = new CookBook({
  name: "SqlfluffCookBook",
  container: ResLayout.vault().join("sqlfluff/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("sqlfluff/"),
    }),
  ],
});

