import { Result } from "@dotfiles/lib/lang.ts";
import { ResLayout } from "@dotfiles/lib/layout.ts";
import { Path } from "@dotfiles/lib/path.ts";
import { PropertyDict, PropertyList } from "@dotfiles/lib/plist.ts";
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

    const plist = new PropertyList({
      path: path.expandHome(),
      root: "New Bookmarks:0",
    });

    const profile = await plist.getDict("");
    if (!profile) {
      options.logger?.info("iTerm 2 profile not found. skip.");
      return;
    }

    {
      const key = "Use Non-ASCII Font";
      const value = true;

      if (profile[key] === value) {
        options.logger?.info(`Non-ASCII Font already enabled: ${value}`);
      } else {
        await plist.setBoolean(key, value, options);
      }
    }

    {
      const key = "Non Ascii Font";
      const value = "HackNFM-Regular 11";

      if (profile[key] === value) {
        options.logger?.info(`Nerd Font already configured: ${value}`);
      } else {
        await plist.setString(key, value, options);
      }
    }

    {
      const key = "Use Separate Colors for Light and Dark Mode";
      const value = false;

      if (profile[key] === value) {
        options.logger?.info(`Separate Colors already disabled: ${value}`);
      } else {
        await plist.setBoolean(key, value, options);
      }
    }

    {
      const key = "Brighten Bold Text";
      const value = true;

      if (profile[key] === value) {
        options.logger?.info(`Brighten Bold Text already enabled: ${value}`);
      } else {
        await plist.setBoolean(key, value, options);
      }
    }

    {
      const key = "Bright Bold";
      const value = true;

      if (profile[key] === value) {
        options.logger?.info(`Bright Bold already enabled: ${value}`);
      } else {
        await plist.setBoolean(key, value, options);
      }
    }

    for (let i = 0; i < 16; i++) {
      const entry = `Ansi ${i} Color`;

      const components = profile[entry] as PropertyDict;
      const preferences = [
        {
          field: "Red Component",
          value: parseInt(theme.Palette[i].slice(1, 3), 16) / 255,
        },
        {
          field: "Green Component",
          value: parseInt(theme.Palette[i].slice(3, 5), 16) / 255,
        },
        {
          field: "Blue Component",
          value: parseInt(theme.Palette[i].slice(5, 7), 16) / 255,
        },
      ];

      const matches = [];
      for (const { field, value } of preferences) {
        const property = components[field] as number;
        if (Math.abs(property - value) < 1 / 255) {
          matches.push({ field: field, value: property });
        } else {
          await plist.setReal(`${entry}:${field}`, value, options);
        }
      }

      if (matches.length === preferences.length) {
        const value = `[${matches.map((x) => x.value).join(", ")}]`;
        options.logger?.info(`${entry} already configured: ${value}`);
      } else {
        for (const { field, value } of matches) {
          options.logger?.info(`${entry} (${field}) already configured: ${value}`);
        }
      }
    }

    for (const key in profile) {
      if (key.includes("(Light)") || key.includes("(Dark)")) {
        await plist.remove(key, options);
      }
    }
  },
  platforms: ["darwin"],
});
