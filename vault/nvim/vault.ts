import { Result } from "@dotfiles/lib/lang.ts";
import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";
import * as vi from "@dotfiles/vault/vi/mod.ts";

export const NeovimCookBook = new CookBook({
  name: "NeovimCookBook",
  container: ResLayout.vault().join("nvim/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("nvim/"),
    }),
  ],
  setup: async (options: shell.CallOptions) => {
    const scheme = vi.Muniere;

    const content = scheme.render();
    const dst = ResLayout.vault().join("nvim", "default", "colors", `${scheme.name}.vim`);

    options.logger?.debug(
      `Create a file ${dst} with content:\n${content}`,
    );

    if (options.dryRun == true) {
      return;
    }

    await Deno.writeTextFile(dst.toFileUrl(), content + "\n");
  },
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
