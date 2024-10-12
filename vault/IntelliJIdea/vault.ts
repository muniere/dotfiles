import { ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

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
  platforms: ["darwin"],
});
