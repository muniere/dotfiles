import { ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import { IdeaColorSchemeDocument } from "@dotfiles/lib/idea.ts";
import * as shell from "@dotfiles/lib/shell.ts";
import * as theme from "@dotfiles/lib/theme.ts";

export const IntelliJIdeaCookBook = new CookBook({
  name: "IntelliJCookBook",
  container: ResLayout.vault().join("IntelliJIdea/"),
  prefs: [
    ...PrefSpec.globp({
      src: ".",
      dst: "~/Library/ApplicationSupport/JetBrains/IntelliJIdea*",
      children: ["colors", "keymaps"],
    }),
  ],
  activate: async (options: shell.CallOptions) => {
    const path = ResLayout.vault().join("IntelliJIdea/darwin/colors/Monokai.icls");
    const source = await Deno.readTextFile(path.toString());

    const doc = IdeaColorSchemeDocument.parse(source);
    doc.applyDefaults({
      "BLOCK_TERMINAL_DEFAULT_FOREGROUND": theme.Palette[7],
    });
    doc.applyAttributes({
      "BLOCK_TERMINAL_BLACK": theme.Palette[0],
      "BLOCK_TERMINAL_RED": theme.Palette[1],
      "BLOCK_TERMINAL_GREEN": theme.Palette[2],
      "BLOCK_TERMINAL_YELLOW": theme.Palette[3],
      "BLOCK_TERMINAL_BLUE": theme.Palette[4],
      "BLOCK_TERMINAL_MAGENTA": theme.Palette[5],
      "BLOCK_TERMINAL_CYAN": theme.Palette[6],
      "BLOCK_TERMINAL_WHITE": theme.Palette[7],
      "BLOCK_TERMINAL_BLACK_BRIGHT": theme.Palette[8],
      "BLOCK_TERMINAL_RED_BRIGHT": theme.Palette[9],
      "BLOCK_TERMINAL_GREEN_BRIGHT": theme.Palette[10],
      "BLOCK_TERMINAL_YELLOW_BRIGHT": theme.Palette[11],
      "BLOCK_TERMINAL_BLUE_BRIGHT": theme.Palette[12],
      "BLOCK_TERMINAL_MAGENTA_BRIGHT": theme.Palette[13],
      "BLOCK_TERMINAL_CYAN_BRIGHT": theme.Palette[14],
      "BLOCK_TERMINAL_WHITE_BRIGHT": theme.Palette[15],
      "CONSOLE_BLACK_OUTPUT": theme.Palette[0],
      "CONSOLE_RED_OUTPUT": theme.Palette[1],
      "CONSOLE_GREEN_OUTPUT": theme.Palette[2],
      "CONSOLE_YELLOW_OUTPUT": theme.Palette[3],
      "CONSOLE_BLUE_OUTPUT": theme.Palette[4],
      "CONSOLE_MAGENTA_OUTPUT": theme.Palette[5],
      "CONSOLE_CYAN_OUTPUT": theme.Palette[6],
      "CONSOLE_WHITE_OUTPUT": theme.Palette[7],
    });

    const result = doc.build({
      trailingNewline: source.endsWith("\n"),
    });

    if (source === result) {
      options.logger?.info(`Color scheme is up-to-date: ${path}`);
      return;
    }

    options.logger?.info(`Color scheme is outdated. Now update: ${path}`);
    if (options.dryRun) {
      return;
    }

    await Deno.writeTextFile(path.toString(), result);
  },
  platforms: ["darwin"],
});
