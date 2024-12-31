import { Eta } from "@eta-dev/eta";

import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import * as theme from "@dotfiles/lib/theme.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const RioCookBook = new CookBook({
  name: "RioCookBook",
  container: ResLayout.vault().join("rio/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("rio/"),
    }),
  ],
  setup: async (options: shell.CallOptions) => {
    const src = ResLayout.vault().join("rio", "template", "themes", "muniere.toml");
    const dst = ResLayout.vault().join("rio", "default", "themes", "muniere.toml");
    const template = await Deno.readTextFile(src.toFileUrl());
    const content = new Eta({ autoTrim: [false, false] }).renderString(template, theme.Palette);

    options.logger?.debug(
      `Create a file ${dst} with content:\n${content}`,
    );

    if (options.dryRun == true) {
      return;
    }

    await Deno.writeTextFile(dst.toFileUrl(), content);
  },
});
