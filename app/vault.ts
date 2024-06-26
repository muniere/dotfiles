import { CookBook, PrefSpec, TmplSpec } from "./schema.ts";
import { HomeLayout } from "./layout.ts";
import { Result } from "./lang.ts";
import { Path } from "./path.ts";
import { PlistBuddy } from "./plist.ts";

import * as shell from "./shell.ts";

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
    new PrefSpec({
      src: "zsh-site-functions/",
      dst: HomeLayout.data().join("zsh/site-functions/"),
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

export const NeovimCookBook = new CookBook({
  name: "NeovimCookBook",
  prefs: [
    new PrefSpec({
      src: "nvim/",
      dst: HomeLayout.config().join("nvim/"),
    }),
  ],
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

export const GitCookBook = new CookBook({
  name: "GitCookBook",
  prefs: [
    new PrefSpec({
      src: "git/",
      dst: HomeLayout.config().join("git/"),
    }),
    new PrefSpec({
      src: "tig/",
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

export const GitHubCookBook = new CookBook({
  name: "GitHubCookBook",
  prefs: [
    new PrefSpec({
      src: "gh/",
      dst: HomeLayout.data().join("gh/"),
    }),
  ],
});

export const AsdfCookBook = new CookBook({
  name: "AsdfCookBook",
  prefs: [
    new PrefSpec({
      src: "asdf/",
      dst: HomeLayout.config().join("asdf/"),
    }),
  ],
});

export const TmuxCookBook = new CookBook({
  name: "TmuxCookBook",
  prefs: [
    new PrefSpec({
      src: "tmux/",
      dst: HomeLayout.config().join("tmux/"),
    }),
  ],
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

export const RubyCookBook = new CookBook({
  name: "RubyCookBook",
  prefs: [
    new PrefSpec({
      src: "bundle/",
      dst: HomeLayout.config().join("bundle/"),
    }),
  ],
});

export const NodeCookBook = new CookBook({
  name: "NodeCookBook",
  prefs: [
    new PrefSpec({
      src: "npm/",
      dst: HomeLayout.config().join("npm/"),
    }),
  ],
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
      src: "cask/Xcode/UserData/FontAndColorThemes/",
      dst: "~/Library/Developer/Xcode/UserData/FontAndColorThemes/",
    }),
    new PrefSpec({
      src: "cask/Xcode/UserData/KeyBindings/",
      dst: "~/Library/Developer/Xcode/UserData/KeyBindings/",
    }),
  ],
  platforms: ["darwin"],
});

export const IntelliJCookBook = new CookBook({
  name: "IntelliJCookBook",
  prefs: [
    ...PrefSpec.globp({
      src: "cask/IntelliJIdea/",
      dst: "~/Library/ApplicationSupport/JetBrains/IntelliJIdea*",
      children: ["colors/", "keymaps/"],
    }),
  ],
  platforms: ["darwin"],
});

export const AndroidStudioCookBook = new CookBook({
  name: "AndroidStudioCookBook",
  prefs: [
    ...PrefSpec.globp({
      src: "cask/AndroidStudio/",
      dst: "~/Library/ApplicationSupport/Google/AndroidStudio*",
      children: ["colors/", "keymaps/"]
    }),
  ],
  platforms: ["darwin"],
});
