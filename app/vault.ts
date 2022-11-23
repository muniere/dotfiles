import { CookBook, PrefRecipe, SnipRecipe } from "./schema.ts";
import { HomeLayout } from "./layout.ts";
import { Result } from "./lang.ts";

import * as shell from "./shell.ts";
import { Path } from "./path.ts";

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
      await shell.mkdirp(dir.path, { ...options, mode: dir.mode });
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
    new PrefRecipe({
      src: "bin/",
      dst: HomeLayout.bin(),
    }),
  ],
});

export const ShCookBook = new CookBook({
  name: "ShCookBook",
  prefs: [
    new PrefRecipe({
      src: "sh/",
      dst: HomeLayout.config().join("sh/"),
    }),
  ],
});

export const BashCookBook = new CookBook({
  name: "BashCookBook",
  prefs: [
    new PrefRecipe({
      src: "bash/",
      dst: HomeLayout.config().join("bash/"),
    }),
  ],
  snips: [
    new SnipRecipe({
      src: "bashrc",
      dst: "~/.bashrc",
    }),
  ],
});

export const ZshCookBook = new CookBook({
  name: "ZshCookBook",
  prefs: [
    new PrefRecipe({
      src: "zsh/",
      dst: HomeLayout.config().join("zsh/"),
    }),
    new PrefRecipe({
      src: "zsh-site-functions/",
      dst: HomeLayout.data().join("zsh/site-functions/"),
    }),
  ],
  snips: [
    new SnipRecipe({
      src: "zshenv",
      dst: "~/.zshenv",
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const url = "https://git.io/zinit-install";
    const path = await Deno.makeTempFile();

    await shell.curl(url, {
      ...options,
      output: path,
    });

    await shell.call(["bash", path], {
      env: {
        "NO_EMOJI": "1",
        "NO_EDIT": "1",
        "NO_TUTORIAL": "1",
      },
      dryRun: options.dryRun,
      logger: options.logger,
    });

    try {
      await shell.which("zsh");
    } catch {
      options.logger?.warn("skip updating zsh plugins. command not found: zsh");
      return;
    }

    await shell.call(["zsh", "-i", "-c", "zinit update --all"], options);
  },
});

export const VimCookBook = new CookBook({
  name: "VimCookBook",
  prefs: [
    new PrefRecipe({
      src: "vim/",
      dst: HomeLayout.config().join("vim/"),
    }),
  ],
  snips: [
    new SnipRecipe({
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

export const GitCookBook = new CookBook({
  name: "GitCookBook",
  prefs: [
    new PrefRecipe({
      src: "git/",
      dst: HomeLayout.config().join("git/"),
    }),
    new PrefRecipe({
      src: "tig/",
      dst: HomeLayout.config().join("tig/"),
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const dir = HomeLayout.data().join("tig");
    const file = dir.join("history");

    const stat = Result.runAsyncOr(() => dir.stat());
    if (!stat) {
      await shell.mkdirp(dir, options);
    }

    shell.touch(file, options);
  },
});

export const GitHubCookBook = new CookBook({
  name: "GitHubCookBook",
  prefs: [
    new PrefRecipe({
      src: "gh/",
      dst: HomeLayout.data().join("gh/"),
    }),
  ],
});

export const AsdfCookBook = new CookBook({
  name: "AsdfCookBook",
  prefs: [
    new PrefRecipe({
      src: "asdf/",
      dst: HomeLayout.config().join("asdf/"),
    }),
  ],
});

export const TmuxCookBook = new CookBook({
  name: "TmuxCookBook",
  prefs: [
    new PrefRecipe({
      src: "tmux/",
      dst: HomeLayout.config().join("tmux/"),
    }),
  ],
});

export const RangerCookBook = new CookBook({
  name: "RangerCookBook",
  prefs: [
    new PrefRecipe({
      src: "ranger/",
      dst: HomeLayout.config().join("ranger/"),
    }),
  ],
});

export const DockerCookBook = new CookBook({
  name: "DockerCookBook",
  prefs: [
    new PrefRecipe({
      src: "/Applications/Docker.app/Contents/Resources/etc/docker.bash-completion",
      dst: HomeLayout.data().join("bash/bash_completion.d/docker"),
    }),
    new PrefRecipe({
      src: "/Applications/Docker.app/Contents/Resources/etc/docker-compose.bash-completion",
      dst: HomeLayout.data().join("bash/bash_completion.d/docker-compose"),
    }),
    new PrefRecipe({
      src: "/Applications/Docker.app/Contents/Resources/etc/docker.zsh-completion",
      dst: HomeLayout.data().join("zsh/site-functions/_docker"),
    }),
    new PrefRecipe({
      src: "/Applications/Docker.app/Contents/Resources/etc/docker-compose.zsh-completion",
      dst: HomeLayout.data().join("zsh/site-functions/_docker-compose"),
    }),
  ],
  platforms: ["darwin"],
});

export const GradleCookBook = new CookBook({
  name: "GradleCookBook",
  prefs: [
    new PrefRecipe({
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
    new PrefRecipe({
      src: "python/",
      dst: HomeLayout.config().join("python/"),
    }),
  ],
});

export const RubyCookBook = new CookBook({
  name: "RubyCookBook",
  prefs: [
    new PrefRecipe({
      src: "bundle/",
      dst: HomeLayout.config().join("bundle/"),
    }),
  ],
});

export const NodeCookBook = new CookBook({
  name: "NodeCookBook",
  prefs: [
    new PrefRecipe({
      src: "npm/",
      dst: HomeLayout.config().join("npm/"),
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const dir = HomeLayout.data().join("node");
    const file = dir.join("history");

    const stat = Result.runAsyncOr(() => dir.stat());
    if (!stat) {
      await shell.mkdirp(dir, options);
    }

    shell.touch(file, options);
  },
});

export const XcodeCookBook = new CookBook({
  name: "XcodeCookBook",
  prefs: [
    new PrefRecipe({
      src: "cask/Xcode/",
      dst: "~/Library/Developer/Xcode/",
    }, {
      autoclean: false,
    }),
  ],
  platforms: ["darwin"],
});

export const IntelliJCookBook = new CookBook({
  name: "IntelliJCookBook",
  prefs: [
    ...PrefRecipe.glob({
      src: "cask/IntelliJIdea/",
      dst: "~/Library/Preferences/IntelliJIdea*",
    }, {
      autoclean: false,
    }),
    ...PrefRecipe.glob({
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
    ...PrefRecipe.glob({
      src: "cask/AndroidStudio/",
      dst: "~/Library/Preferences/AndroidStudio*",
    }, {
      autoclean: false,
    }),
    ...PrefRecipe.glob({
      src: "cask/AndroidStudio/",
      dst: "~/Library/ApplicationSupport/Google/AndroidStudio*",
    }, {
      autoclean: false,
    }),
  ],
  platforms: ["darwin"],
});

export const AppCodeCookBook = new CookBook({
  name: "AppCodeCookBook",
  prefs: [
    ...PrefRecipe.glob({
      src: "cask/AppCode/",
      dst: "~/Library/Preferences/AppCode*",
    }, {
      autoclean: false,
    }),
    ...PrefRecipe.glob({
      src: "cask/AppCode/",
      dst: "~/Library/ApplicationSupport/JetBrains/AppCode*",
    }, {
      autoclean: false,
    }),
  ],
  platforms: ["darwin"],
});

export const RubyMineCookBook = new CookBook({
  name: "RubyMineCookBook",
  prefs: [
    ...PrefRecipe.glob({
      src: "cask/RubyMine/",
      dst: "~/Library/Preferences/RubyMine*",
    }, {
      autoclean: false,
    }),
    ...PrefRecipe.glob({
      src: "cask/RubyMine/",
      dst: "~/Library/ApplicationSupport/JetBrains/RubyMine*",
    }, {
      autoclean: false,
    }),
  ],
  platforms: ["darwin"],
});

export const GoLandCookBook = new CookBook({
  name: "GoLandCookBook",
  prefs: [
    ...PrefRecipe.glob({
      src: "cask/GoLand/",
      dst: "~/Library/Preferences/GoLand*",
    }),
    ...PrefRecipe.glob({
      src: "cask/GoLand/",
      dst: "~/Library/ApplicationSupport/JetBrains/GoLand*",
    }),
  ],
  platforms: ["darwin"],
});

export const CLionCookBook = new CookBook({
  name: "CLionCookBook",
  prefs: [
    ...PrefRecipe.glob({
      src: "cask/CLion/",
      dst: "~/Library/Preferences/CLion*",
    }),
    ...PrefRecipe.glob({
      src: "cask/CLion/",
      dst: "~/Library/ApplicationSupport/JetBrains/CLion*",
    }),
  ],
  platforms: ["darwin"],
});

export const RiderCookBook = new CookBook({
  name: "RiderCookBook",
  prefs: [
    ...PrefRecipe.glob({
      src: "cask/Rider/",
      dst: "~/Library/Preferences/Rider*",
    }, {
      autoclean: false,
    }),
    ...PrefRecipe.glob({
      src: "cask/Rider/",
      dst: "~/Library/ApplicationSupport/JetBrains/Rider*",
    }, {
      autoclean: false,
    }),
  ],
  platforms: ["darwin"],
});
