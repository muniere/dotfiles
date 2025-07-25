import { Eta } from "@eta-dev/eta";

import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import * as theme from "@dotfiles/lib/theme.ts";
import * as shell from "@dotfiles/lib/shell.ts";

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
    // template
    {
      const src = ResLayout.vault().join("ghostty", "template", "themes", "muniere");
      const dst = ResLayout.vault().join("ghostty", "default", "themes", "muniere");
      const template = await Deno.readTextFile(src.toFileUrl());
      const content = new Eta({ autoTrim: [false, false] }).renderString(template, theme.Palette);

      options.logger?.debug(
        `Create a file ${dst} with content:\n${content}`,
      );

      if (options.dryRun !== true) {
        await Deno.writeTextFile(dst.toFileUrl(), content);
      }
    }

    // config
    {
      const dir = HomeLayout.config().join("ghostty", "conf.d");
      const file = dir.join("local.ghostrc");

      if (options.dryRun !== true) {
        await Deno.mkdir(dir.toFileUrl(), { recursive: true });
      }

      try {
        if (options.dryRun !== true) {
          await Deno.writeTextFile(file.toFileUrl(), "", { createNew: true });
        }

        options.logger?.debug(`Create a file ${file} with empty content`);
      } catch (error) {
        if (!(error instanceof Deno.errors.AlreadyExists)) {
          throw error;
        }
      }
    }
  },
});
