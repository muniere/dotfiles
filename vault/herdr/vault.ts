// herdr: terminal workspace manager for AI coding agents.
// Reference: https://herdr.dev/docs/configuration/
import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const HerdrCookBook = new CookBook({
  name: "HerdrCookBook",
  container: ResLayout.vault().join("herdr/"),
  prefs: [
    new PrefSpec({
      src: "conf.d/",
      dst: HomeLayout.config().join("herdr/"),
    }),
    new PrefSpec({
      src: "bin/",
      dst: HomeLayout.bin(),
    }),
    new PrefSpec({
      src: "completion/",
      dst: HomeLayout.data().join("zsh/site-functions/"),
    }),
  ],
});
