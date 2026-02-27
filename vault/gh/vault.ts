import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const GitHubCookBook = new CookBook({
  name: "GitHubCookBook",
  container: ResLayout.vault().join("gh/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.data().join("gh/"),
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const repos = [
      "muniere/gh-team",
    ];

    const which = await shell.capture("which", ["gh"]);
    const cmd = which.stdout.trim();
    if (which.status.code !== 0 || !cmd) {
      options.logger?.warn("gh not found on PATH yet. skip.");
      return;
    }

    for (const repo of repos) {
      await shell.call(cmd, ["extension", "install", repo], options);
    }
  },
});
