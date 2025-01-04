import { Result } from "@dotfiles/lib/lang.ts";
import { ResLayout } from "@dotfiles/lib/layout.ts";
import { Path } from "@dotfiles/lib/path.ts";
import { PlistBuddy, PropertyDict } from "@dotfiles/lib/plist.ts";
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
      root: "New Bookmarks:0",
    });

    const profile = await buddy.getDict("");
    if (!profile) {
      options.logger?.info("iTerm 2 profile not found. skip.");
      return;
    }

    {
      const key = "Use Non-ASCII Font";
      const value = true;

      if (profile[key] === value) {
        options.logger?.info(`Nerd Font already enabled: ${value}`);
      } else {
        await buddy.setBoolean(key, value, options);
      }
    }

    {
      const key = "Non Ascii Font";
      const value = "HackNFM-Regular 11";

      if (profile[key] === value) {
        options.logger?.info(`Nerd Font already configured: ${value}`);
      } else {
        await buddy.setString(key, value, options);
      }
    }

    {
      const keys = [
        "Brighten Bold Text (Light)",
        "Brighten Bold Text (Dark)",
      ];
      const value = false;

      for (const key of keys) {
        if (profile[key] === value) {
          options.logger?.info(`${key} already configured: ${value}`);
        } else {
          await buddy.setBoolean(key, value, options);
        }
      }
    }

    for (let i = 0; i < 16; i++) {
      const entries = [
        `Ansi ${i} Color`,
        `Ansi ${i} Color (Light)`,
        `Ansi ${i} Color (Dark)`,
      ];

      for (const entry of entries) {
        const components = profile[entry] as PropertyDict;

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
          const field = "Red Component";
          const value = red;

          const property = components[field] as number;
          if (Math.abs(property - value) < 1 / 255) {
            hits.push({ key: "red", value: property });
          } else {
            await buddy.setReal(`${entry}:${field}`, value, options);
          }
        }

        // green
        {
          const field = `Green Component`;
          const value = green;

          const property = components[field] as number;
          if (Math.abs(property - value) < 1 / 255) {
            hits.push({ key: "green", value: property });
          } else {
            await buddy.setReal(`${entry}:${field}`, value, options);
          }
        }

        // blue
        {
          const field = `Blue Component`;
          const value = blue;

          const property = components[field] as number;
          if (Math.abs(property - value) < 0.004) {
            hits.push({ key: "blue", value: property });
          } else {
            await buddy.setReal(`${entry}:${field}`, value, options);
          }
        }

        if (hits.length === 3) {
          const value = `[${hits.map((x) => x.value).join(", ")}]`;
          options.logger?.info(`${entry} already configured: ${value}`);
          continue;
        }

        for (const hit of hits) {
          options.logger?.info(`${entry} (${hit.key}) already configured: ${hit.value}`);
        }
      }
    }
  },
  platforms: ["darwin"],
});
