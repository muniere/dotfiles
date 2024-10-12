import { Result } from "@dotfiles/lib/lang.ts";
import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const NodeCookBook = new CookBook({
  name: "NodeCookBook",
  container: ResLayout.vault().join("node/"),
  activate: async (options: shell.CallOptions) => {
    const dir = HomeLayout.data().join("node");
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
