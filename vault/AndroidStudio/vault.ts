import { ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

export const AndroidStudioCookBook = new CookBook({
  name: "AndroidStudioCookBook",
  container: ResLayout.vault().join("AndroidStudio/"),
  prefs: [
    ...PrefSpec.globp({
      src: ".",
      dst: "~/Library/ApplicationSupport/Google/AndroidStudio*",
      children: ["colors", "keymaps"],
    }),
  ],
  platforms: ["darwin"],
});
