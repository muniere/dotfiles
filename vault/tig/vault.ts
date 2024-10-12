import { Result } from "@dotfiles/lib/lang.ts";
import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const TigCookBook = new CookBook({
  name: "TigCookBook",
  container: ResLayout.vault().join("tig/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("tig/"),
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const dir = HomeLayout.data().join("tig");
    const file = dir.join("history");

    const dstat = await Result.runAsyncOr(() => dir.stat());
    if (dstat) {
      // do nothing, and do not output logs
    } else {
      await shell.mkdir(dir, options);
    }

    const fstat = await Result.runAsyncOr(() => file.stat());
    if (fstat) {
      options.logger?.info(`File already exists: ${file}`);
    } else {
      await shell.touch(file, options);
    }
  },
});
