import { Result } from "../lib/lang.ts";
import { HomeLayout } from "../lib/layout.ts";
import { Path } from "../lib/path.ts";
import { PlistBuddy } from "../lib/plist.ts";
import { CookBook, PrefSpec, TmplSpec } from "../lib/schema.ts";

import * as shell from "../lib/shell.ts";

export { AsdfCookBook } from "../vault/asdf/vault.ts";
export { GitCookBook } from "../vault/git/vault.ts";
export { GitHubCookBook } from "../vault/gh/vault.ts";
export { NeovimCookBook } from "../vault/nvim/vault.ts";
export { TigCookBook } from "../vault/tig/vault.ts";
export { TmuxCookBook } from "../vault/tmux/vault.ts";

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

export const BinCookBook = new CookBook({
  name: "BinCookBook",
  prefs: [
    new PrefSpec({
      src: "bin/",
      dst: HomeLayout.bin(),
    }),
  ],
});

export const ShCookBook = new CookBook({
  name: "ShCookBook",
  prefs: [
    new PrefSpec({
      src: "sh/",
      dst: HomeLayout.config().join("sh/"),
    }),
  ],
});

export const BashCookBook = new CookBook({
  name: "BashCookBook",
  prefs: [
    new PrefSpec({
      src: "bash/",
      dst: HomeLayout.config().join("bash/"),
    }),
  ],
  tmpls: [
    new TmplSpec({
      src: "bashrc",
      dst: "~/.bashrc",
    }, {
      values: {
        cache: HomeLayout.cache().transHome(),
        config: HomeLayout.config().transHome(),
        data: HomeLayout.data().transHome(),
        state: HomeLayout.state().transHome(),
        runtime: HomeLayout.runtime().transHome(),
      },
    }),
  ],
});

export const ZshCookBook = new CookBook({
  name: "ZshCookBook",
  prefs: [
    new PrefSpec({
      src: "zsh/",
      dst: HomeLayout.config().join("zsh/"),
    }),
  ],
  tmpls: [
    new TmplSpec({
      src: "zshenv",
      dst: "~/.zshenv",
    }, {
      values: {
        cache: HomeLayout.cache().transHome(),
        config: HomeLayout.config().transHome(),
        data: HomeLayout.data().transHome(),
        state: HomeLayout.state().transHome(),
        runtime: HomeLayout.runtime().transHome(),
      },
    }),
  ],
});

export const ZshSiteFunctionsCookBook = new CookBook({
  name: "ZshSiteFunctionsCookBook",
  prefs: [
    new PrefSpec({
      src: "zsh-site-functions/",
      dst: HomeLayout.data().join("zsh/site-functions/"),
    }),
  ],
});

export const VimCookBook = new CookBook({
  name: "VimCookBook",
  prefs: [
    new PrefSpec({
      src: "vim/",
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

export const YaziCookBook = new CookBook({
  name: "YaziCookBook",
  prefs: [
    new PrefSpec({
      src: "yazi/",
      dst: HomeLayout.config().join("yazi/"),
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const dir = HomeLayout.config().join("yazi/plugins");

    const dstat = await Result.runAsyncOr(() => dir.stat());
    if (dstat) {
      // do nothing, and do not output logs
    } else {
      await shell.mkdir(dir, options);
    }

    const packages = [
      // https://github.com/yazi-rs/plugins/tree/main/full-border.yazi
      {
        name: "full-border",
        src: "yazi-rs/plugins:full-border",
        dest: "full-border.yazi",
      },
    ];

    const which = await shell.capture("which", ["ya"]);
    const cmd = which.stdout.trim();
    if (which.status.code !== 0 || !cmd) {
      options.logger?.warn("yazi not found on PATH yet. skip.");
      return;
    }

    const entries = await Array.fromAsync(dir.readDir());
    const installed = new Set(entries.map((it) => it.name));

    for (const pkg of packages) {
      if (installed.has(pkg.dest)) {
        options.logger?.info(`Plugin already installed: ${pkg.name}`);
      } else {
        await shell.call(cmd, ["pack", "-a", pkg.src], options);
      }
    }
  },
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

export const PythonCookBook = new CookBook({
  name: "PythonCookBook",
  prefs: [
    new PrefSpec({
      src: "python/",
      dst: HomeLayout.config().join("python/"),
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
