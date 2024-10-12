import { Result } from "@dotfiles/lib/lang.ts";
import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const NeovimCookBook = new CookBook({
  name: "NeovimCookBook",
  container: ResLayout.vault().join("nvim/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("nvim/"),
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const url = "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim";
    const path = HomeLayout.data().join("nvim/site/autoload/plug.vim");

    const stat = await Result.runAsyncOr(() => path.stat());
    if (stat) {
      options.logger?.info(`File already exists: ${path}`);
      return;
    }

    await shell.curl(url, { ...options, output: path });
  },
});
