import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const GinCookBook = new CookBook({
  name: "GinCookBook",
  container: ResLayout.vault().join("gin/"),
  prefs: [
    new PrefSpec({
      src: "./zsh/gin.zsh",
      dst: HomeLayout.config().join("zsh/rc.d/750_gin.rc.zsh"),
    }),
    new PrefSpec({
      src: "./zsh/site-functions/_gin",
      dst: HomeLayout.data().join("zsh/site-functions/_gin"),
    }),
  ],
});
