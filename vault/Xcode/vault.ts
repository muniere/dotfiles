import { ResLayout } from "../../lib/layout.ts";
import { CookBook, PrefSpec } from "../../lib/schema.ts";

export const XcodeCookBook = new CookBook({
  name: "XcodeCookBook",
  container: ResLayout.vault().join("Xcode/"),
  prefs: [
    new PrefSpec({
      src: "./UserData/FontAndColorThemes",
      dst: "~/Library/Developer/Xcode/UserData/FontAndColorThemes",
    }),
    new PrefSpec({
      src: "./UserData/KeyBindings",
      dst: "~/Library/Developer/Xcode/UserData/KeyBindings",
    }),
  ],
  platforms: ["darwin"],
});
