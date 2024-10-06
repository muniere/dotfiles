import { Result } from "../lib/lang.ts";
import { HomeLayout } from "../lib/layout.ts";
import { Path } from "../lib/path.ts";
import { CookBook, PrefSpec } from "../lib/schema.ts";

import * as shell from "../lib/shell.ts";

export { AsdfCookBook } from "../vault/asdf/vault.ts";
export { BashCookBook } from "../vault/bash/vault.ts";
export { BinCookBook } from "../vault/bin/vault.ts";
export { DockerCookBook } from "../vault/docker/vault.ts";
export { GitCookBook } from "../vault/git/vault.ts";
export { GitHubCookBook } from "../vault/gh/vault.ts";
export { iTermCookBook } from "../vault/iterm/vault.ts";
export { IntelliJIdeaCookBook } from "../vault/IntelliJIdea/vault.ts";
export { NeovimCookBook } from "../vault/nvim/vault.ts";
export { NodeCookBook } from "../vault/node/vault.ts";
export { PythonCookBook } from "../vault/python/vault.ts";
export { ShCookBook } from "../vault/sh/vault.ts";
export { TigCookBook } from "../vault/tig/vault.ts";
export { TmuxCookBook } from "../vault/tmux/vault.ts";
export { VimCookBook } from "../vault/vim/vault.ts";
export { YaziCookBook } from "../vault/yazi/vault.ts";
export { XcodeCookBook } from "../vault/Xcode/vault.ts";
export { ZshCookBook } from "../vault/zsh/vault.ts";
export { ZshSiteFunctionsCookBook } from "../vault/zsh-site-functions/vault.ts";

export const HomeCookBook = new CookBook({
  name: "HomeCookBook",
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

export const GradleCookBook = new CookBook({
  name: "GradleCookBook",
  prefs: [
    new PrefSpec({
      src: "gradle/gradle.properties",
      dst: HomeLayout.data().join("gradle/gradle.properties"),
    }, {
      kind: "copy",
      autoclean: false,
    }),
  ],
});

export const AndroidStudioCookBook = new CookBook({
  name: "AndroidStudioCookBook",
  prefs: [
    ...PrefSpec.glob({
      src: "cask/AndroidStudio/",
      dst: "~/Library/ApplicationSupport/Google/AndroidStudio*",
    }, {
      autoclean: false,
    }),
  ],
  platforms: ["darwin"],
});
