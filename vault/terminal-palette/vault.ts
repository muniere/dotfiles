import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook } from "@dotfiles/lib/schema.ts";
import { Result } from "@dotfiles/lib/lang.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const TerminalPaletteCookBook = new CookBook({
  name: "TerminalPaletteCookBook",
  container: ResLayout.vault().join("terminal-palette/"),
  setup: async (options) => {
    const url = "https://raw.githubusercontent.com/mgedmin/scripts/refs/heads/master/show-all-256-colors";
    const path = HomeLayout.bin().join("terminal-palette");

    const stat = await Result.runAsyncOr(() => path.stat());
    if (stat) {
      options.logger?.info(`File already exists: ${path}`);
      return;
    }

    await shell.curl(url, { ...options, output: path });
    await shell.chmod(path, "+x", {...options});
  },
});
