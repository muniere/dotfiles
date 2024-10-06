import { Result } from "../lib/lang.ts";
import { HomeLayout } from "../lib/layout.ts";
import { Path } from "../lib/path.ts";
import { PlistBuddy } from "../lib/plist.ts";
import { CookBook, PrefSpec } from "../lib/schema.ts";

import * as shell from "../lib/shell.ts";

export { AsdfCookBook } from "../vault/asdf/vault.ts";
export { BashCookBook } from "../vault/bash/vault.ts";
export { BinCookBook } from "../vault/bin/vault.ts";
export { GitCookBook } from "../vault/git/vault.ts";
export { GitHubCookBook } from "../vault/gh/vault.ts";
export { NeovimCookBook } from "../vault/nvim/vault.ts";
export { PythonCookBook } from "../vault/python/vault.ts";
export { ShCookBook } from "../vault/sh/vault.ts";
export { TigCookBook } from "../vault/tig/vault.ts";
export { TmuxCookBook } from "../vault/tmux/vault.ts";
export { VimCookBook } from "../vault/vim/vault.ts";
export { YaziCookBook } from "../vault/yazi/vault.ts";
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

const DockerResDir = new Path("/Applications/Docker.app/Contents/Resources");

export const DockerCookBook = new CookBook({
  name: "DockerCookBook",
  prefs: [
    new PrefSpec({
      src: DockerResDir.join("etc/docker.bash-completion"),
      dst: HomeLayout.data().join("bash/bash_completion.d/docker"),
    }),
    new PrefSpec({
      src: DockerResDir.join("etc/docker-compose.bash-completion"),
      dst: HomeLayout.data().join("bash/bash_completion.d/docker-compose"),
    }),
    new PrefSpec({
      src: DockerResDir.join("etc/docker.zsh-completion"),
      dst: HomeLayout.data().join("zsh/site-functions/_docker"),
    }),
    new PrefSpec({
      src: DockerResDir.join("etc/docker-compose.zsh-completion"),
      dst: HomeLayout.data().join("zsh/site-functions/_docker-compose"),
    }),
  ],
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

export const NodeCookBook = new CookBook({
  name: "NodeCookBook",
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

export const iTermCookBook = new CookBook({
  name: "iTermCookBook",
  prefs: [],
  activate: async (options: shell.CallOptions) => {
    const path = new Path("~/Library/Preferences/com.googlecode.iterm2.plist").expandHome();

    const stat = await Result.runAsyncOr(() => path.lstat());
    if (!stat) {
      options.logger?.info("iTerm 2 not installed yet. skip.");
      return;
    }

    const buddy = new PlistBuddy({
      path: path.expandHome(),
    });

    {
      const key = "New Bookmarks:0:Use Non-ASCII Font";
      const value = true;

      const result = await buddy.getBoolean(key);
      if (result === value) {
        options.logger?.info(`Nerd Font already enabled: ${value}`);
      } else {
        await buddy.setBoolean(key, value, options);
      }
    }

    {
      const key = "New Bookmarks:0:Non Ascii Font";
      const value = "HackNerdFontComplete-Regular 12";

      const result = await buddy.getString(key);
      if (result === value) {
        options.logger?.info(`Nerd Font already configured: ${value}`);
      } else {
        await buddy.setString(key, value, options);
      }
    }
  },
  platforms: ["darwin"],
});

export const XcodeCookBook = new CookBook({
  name: "XcodeCookBook",
  prefs: [
    new PrefSpec({
      src: "cask/Xcode/UserData/",
      dst: "~/Library/Developer/Xcode/UserData/",
    }, {
      autoclean: false,
    }),
  ],
  platforms: ["darwin"],
});

export const IntelliJCookBook = new CookBook({
  name: "IntelliJCookBook",
  prefs: [
    ...PrefSpec.glob({
      src: "cask/IntelliJIdea/",
      dst: "~/Library/ApplicationSupport/JetBrains/IntelliJIdea*",
    }, {
      autoclean: false,
    }),
  ],
  platforms: ["darwin"],
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
