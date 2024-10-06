import { Result } from "../../lib/lang.ts";
import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

import * as shell from "../../lib/shell.ts";

export const NeovimCookBook = new CookBook({
  name: "NeovimCookBook",
  prefs: [
    new PrefSpec({
      src: "nvim/",
      dst: HomeLayout.config().join("nvim/"),
    }, {
      layout: "by-component",
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
  container: ResLayout.vault(),
});
