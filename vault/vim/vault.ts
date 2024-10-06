import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { Result } from "../../lib/lang.ts";
import { CookBook, PrefSpec, TmplSpec } from "../../lib/schema.ts";

import * as shell from "../../lib/shell.ts";

export const VimCookBook = new CookBook({
  name: "VimCookBook",
  container: ResLayout.vault().join("vim/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("vim/"),
    }),
  ],
  tmpls: [
    new TmplSpec({
      src: "vimrc",
      dst: "~/.vimrc",
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const url = "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim";
    const path = HomeLayout.config().join("vim/autoload/plug.vim");

    const stat = await Result.runAsyncOr(() => path.stat());
    if (stat) {
      options.logger?.info(`File already exists: ${path}`);
      return;
    }

    await shell.curl(url, { ...options, output: path });
  },
});
