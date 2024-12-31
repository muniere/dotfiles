import { Result } from "@dotfiles/lib/lang.ts";
import { ResLayout } from "@dotfiles/lib/layout.ts";
import { Path } from "@dotfiles/lib/path.ts";
import { PlistBuddy } from "@dotfiles/lib/plist.ts";
import { CookBook } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";
import * as theme from "@dotfiles/lib/theme.ts";

export const iTermCookBook = new CookBook({
  name: "iTermCookBook",
  container: ResLayout.vault().join("iterm/"),
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
      const value = "HackNFM-Regular 11";

      const result = await buddy.getString(key);
      if (result === value) {
        options.logger?.info(`Nerd Font already configured: ${value}`);
      } else {
        await buddy.setString(key, value, options);
      }
    }

    for (let i = 0; i < 16; i++) {
      const prefixes = [
        `New Bookmarks:0:Ansi ${i} Color`,
        `New Bookmarks:0:Ansi ${i} Color (Light)`,
        `New Bookmarks:0:Ansi ${i} Color (Dark)`,
      ];

      for (const prefix of prefixes) {
        const [red, green, blue] = (() => {
          const hex = theme.Palette[i];
          const r = parseInt(hex.slice(1, 3), 16) / 255;
          const g = parseInt(hex.slice(3, 5), 16) / 255;
          const b = parseInt(hex.slice(5, 7), 16) / 255;
          return [r, g, b];
        })();

        const hits = [];

        // red
        {
          const key = `${prefix}:Red Component`;
          const value = red;

          const result = await buddy.getReal(key);
          if (result !== null && Math.abs(result - value) < 1 / 255) {
            hits.push({ key: "red", value: result });
          } else {
            await buddy.setReal(key, value, options);
          }
        }

        // green
        {
          const key = `${prefix}:Green Component`;
          const value = green;

          const result = await buddy.getReal(key);
          if (result !== null && Math.abs(result - value) < 1 / 255) {
            hits.push({ key: "green", value: result });
          } else {
            await buddy.setReal(key, value, options);
          }
        }

        // blue
        {
          const key = `${prefix}:Blue Component`;
          const value = blue;

          const result = await buddy.getReal(key);
          if (result !== null && Math.abs(result - value) < 0.004) {
            hits.push({ key: "blue", value: result });
          } else {
            await buddy.setReal(key, value, options);
          }
        }

        if (hits.length === 3) {
          const value = `[${hits.map((x) => x.value).join(", ")}]`;
          options.logger?.info(`Ansi Color ${i} already configured: ${value}`);
          continue;
        }

        for (const hit of hits) {
          options.logger?.info(`Ansi Color ${i} (${hit.key}) already configured: ${hit.value}`);
        }
      }
    }
  },
  platforms: ["darwin"],
});
