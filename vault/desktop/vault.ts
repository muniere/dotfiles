import { Result } from "@dotfiles/lib/lang.ts";
import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { Path } from "@dotfiles/lib/path.ts";
import { CookBook } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const HomeCookBook = new CookBook({
  name: "HomeCookBook",
  container: ResLayout.vault().join("desktop/"),
  activate: async (options: shell.CallOptions) => {
    const dirs = [
      { path: HomeLayout.bin(), mode: 0o755 },
      { path: HomeLayout.cache(), mode: 0o755 },
      { path: HomeLayout.config(), mode: 0o755 },
      { path: HomeLayout.data(), mode: 0o755 },
      { path: HomeLayout.state(), mode: 0o755 },
      { path: HomeLayout.runtime(), mode: 0o700 },
    ];

    for (const dir of dirs) {
      const stat = await Result.runAsyncOr(() => dir.path.stat());
      if (stat) {
        if (stat.isDirectory) {
          options.logger?.info(`Directory already exists: ${dir.path}`);
        } else {
          options.logger?.warn(`File already exists, not a directory: ${dir.path}`);
        }
        continue;
      }

      await shell.mkdir(dir.path, { ...options, mode: dir.mode });
    }
  },
});

export const LibraryCookBook = new CookBook({
  name: "LibraryCookBook",
  container: ResLayout.vault().join("desktop/"),
  activate: async (options: shell.CallOptions) => {
    const src = new Path("~/Library/Application Support").expandHome();
    const dst = new Path("~/Library/ApplicationSupport").expandHome();

    const stat = await Result.runAsyncOr(() => dst.stat());
    if (stat) {
      if (stat.isDirectory) {
        options.logger?.info(`Directory already exists: ${dst}`);
      } else {
        options.logger?.warn(`File already exists, not a directory: ${dst}`);
      }
      return;
    }

    await shell.symlink(src, dst, options);
  },
  platforms: ["darwin"],
});
