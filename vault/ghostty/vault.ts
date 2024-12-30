import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import * as theme from "@dotfiles/lib/theme.ts";
import * as shell from "@dotfiles/lib/shell.ts";
import { Eta } from "@eta-dev/eta";

export const GhosttyCookBook = new CookBook({
  name: "GhosttyCookBook",
  container: ResLayout.vault().join("ghostty/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("ghostty/"),
    }),
  ],
  setup: async (options: shell.CallOptions) => {
    const src = ResLayout.vault().join("ghostty", "template", "themes", "muniere");
    const dst = ResLayout.vault().join("ghostty", "default", "themes", "muniere");
    const template = await Deno.readTextFile(src.toFileUrl());
    const content = new Eta({autoTrim: [false, false]}).renderString(template, theme.Palette);

    options.logger?.debug(
      `Create a file ${dst} with content:\n${content}`,
    );

    if (options.dryRun == true) {
      return;
    }

    await Deno.writeTextFile(dst.toFileUrl(), content);
  },
});
