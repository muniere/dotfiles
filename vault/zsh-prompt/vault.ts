import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const ZshPromptCookBook = new CookBook({
  name: "ZshPromptCookBook",
  container: ResLayout.vault().join("zsh-prompt/"),
  prefs: [
    new PrefSpec({
      src: "bin/",
      dst: HomeLayout.bin(),
    }),
    new PrefSpec({
      src: "zprompt.zsh",
      dst: HomeLayout.data().join("zsh/prompt/zprompt.zsh"),
    }),
    new PrefSpec({
      src: "themes/",
      dst: HomeLayout.data().join("zsh/prompt/themes/"),
    }),
    new PrefSpec({
      src: "completion/",
      dst: HomeLayout.data().join("zsh/site-functions/"),
    }),
  ],
});
