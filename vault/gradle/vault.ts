import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const GradleCookBook = new CookBook({
  name: "GradleCookBook",
  container: ResLayout.vault().join("gradle/"),
  prefs: [
    new PrefSpec({
      src: "gradle.properties",
      dst: HomeLayout.data().join("gradle/gradle.properties"),
    }, {
      kind: "copy",
      autoclean: false,
    }),
  ],
});
