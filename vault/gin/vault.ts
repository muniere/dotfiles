import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const GinCookBook = new CookBook({
  name: "GinCookBook",
  container: ResLayout.vault().join("gin/"),
  prefs: [
    new PrefSpec({
      src: "./zsh/site-functions/_gin",
      dst: HomeLayout.data().join("zsh/site-functions/_gin"),
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const src = ResLayout.vault().join("gin/default/src");
    const dst = HomeLayout.bin().join("gin");

    const status = await shell.call("go", [
      "build",
      "-o",
      dst.toString(),
      src.join("main.go").toString(),
    ], options);

    if (!status.success) {
      options.logger?.warn("Failed to build gin. Ensure Go is installed.");
    }
  },
});
