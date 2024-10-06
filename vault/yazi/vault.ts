import { HomeLayout, ResLayout } from "../../lib/layout.ts";
import { Result } from "../../lib/lang.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

import * as shell from "../../lib/shell.ts";

export const YaziCookBook = new CookBook({
  name: "YaziCookBook",
  container: ResLayout.vault().join("yazi/"),
  prefs: [
    new PrefSpec({
      src: ".",
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
