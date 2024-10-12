import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const PythonCookBook = new CookBook({
  name: "PythonCookBook",
  container: ResLayout.vault().join("python/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("python/"),
    }),
  ],
});
