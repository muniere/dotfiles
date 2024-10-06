import { Result } from "../../lib/lang.ts";
import { ResLayout } from "../../lib/layout.ts";
import { Path } from "../../lib/path.ts";
import { PlistBuddy } from "../../lib/plist.ts";
import { CookBook } from "../../lib/schema.ts";

import * as shell from "../../lib/shell.ts";

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
      const value = "HackNerdFontComplete-Regular 12";

      const result = await buddy.getString(key);
      if (result === value) {
        options.logger?.info(`Nerd Font already configured: ${value}`);
      } else {
        await buddy.setString(key, value, options);
      }
    }
  },
  platforms: ["darwin"],
});
