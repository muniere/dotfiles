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
      await shell.mkdir(dir.path, { ...options, mode: dir.mode });
    }
  },
});

export const LibraryCookBook = new CookBook({
  name: "LibraryCookBook",
  activate: async (options: shell.CallOptions) => {
    await shell.symlink(
      new Path("~/Library/Application Support").expandHome(),
      new Path("~/Library/ApplicationSupport").expandHome(),
      options,
    );
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
  activate: async (options: shell.CallOptions) => {
    const url = "https://github.com/zsh-users/zsh-syntax-highlighting.git";
    const dir = HomeLayout.data().join("zsh-syntax-highlighting");

    const stat = await Result.runAsyncOr(() => dir.lstat());
    if (stat) {
      await shell.call(["git", "-C", dir.toString(), "pull", "-v"], {
        dryRun: options.dryRun,
        logger: options.logger,
      });
    } else {
      await shell.call(["git", "clone", url, dir.toString(), "-v"], {
        dryRun: options.dryRun,
        logger: options.logger,
      });
    }
  },
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

    await shell.curl(url, {
      ...options,
      output: path,
    });
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

    const stat = Result.runAsyncOr(() => dir.stat());
    if (!stat) {
      await shell.mkdir(dir, options);
    }

    shell.touch(file, options);
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

    const stat = Result.runAsyncOr(() => dir.stat());
    if (!stat) {
      await shell.mkdir(dir, options);
    }

    shell.touch(file, options);
  },
});

export const iTermCookBook = new CookBook({
  name: "iTermCookBook",
  prefs: [],
  activate: async (options: shell.CallOptions) => {
    const path = new Path("~/Library/Preferences/com.googlecode.iterm2.plist").expandHome();
    
    const stat = await Result.runAsyncOr(() => path.lstat());
    if (!stat) {
      options.logger?.info("iTerm 2 not installed yet. skip.")
      return;
    }

    const buddy = new PlistBuddy({
      path: path.expandHome(),
    });

    await buddy.setBoolean(
      "New Bookmarks:0:Use Non-ASCII Font",
      true,
      options,
    );
    await buddy.setString(
      "New Bookmarks:0:Non Ascii Font",
      "HackNerdFontComplete-Regular 12",
      options,
    );
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
    ...PrefSpec.glob({
      src: "cask/IntelliJIdea/colors/",
      dst: "~/Library/ApplicationSupport/JetBrains/IntelliJIdea*/colors/",
    }),
    ...PrefSpec.glob({
      src: "cask/IntelliJIdea/colors/keymaps/",
      dst: "~/Library/ApplicationSupport/JetBrains/IntelliJIdea*/keymaps/",
    }),
  ],
  platforms: ["darwin"],
});

export const AndroidStudioCookBook = new CookBook({
  name: "AndroidStudioCookBook",
  prefs: [
    ...PrefSpec.glob({
      src: "cask/AndroidStudio/colors/",
      dst: "~/Library/ApplicationSupport/Google/AndroidStudio*/colors/",
    }),
    ...PrefSpec.glob({
      src: "cask/AndroidStudio/keymaps/",
      dst: "~/Library/ApplicationSupport/Google/AndroidStudio*/keymaps/",
    }),
  ],
  platforms: ["darwin"],
});
