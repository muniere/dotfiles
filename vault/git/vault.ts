import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import { Result } from "@dotfiles/lib/lang.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const GitCookBook = new CookBook({
  name: "GitCookBook",
  container: ResLayout.vault().join("git/"),
  prefs: [
    new PrefSpec({
      src: "config",
      dst: HomeLayout.config().join("git/config"),
    }),
    new PrefSpec({
      src: "conf.d",
      dst: HomeLayout.config().join("git/conf.d/"),
    }),
    new PrefSpec({
      src: "bin",
      dst: HomeLayout.bin(),
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const dir = HomeLayout.config().join("git/conf.d/");
    const file = dir.join("config.extension");

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
