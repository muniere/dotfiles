import { ResLayout } from "@dotfiles/lib/layout.ts";
import { Path } from "@dotfiles/lib/path.ts";
import { CookBook } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const CodeCookBook = new CookBook({
  name: "CodeCookBook",
  container: ResLayout.vault().join("Code/"),
  activate: async (options: shell.CallOptions) => {
    const container = ResLayout.vault().join("Code/default/muniere-vscode-theme");
    const manifest = await CodeExtensions.info(container);

    const installed = await CodeExtensions.find({
      publisher: manifest.publisher,
      name: manifest.name,
    });

    if (installed && installed.version === manifest.version) {
      options.logger?.info(
        `Extension already installed: ${installed.publisher}.${installed.name}@${installed.version}`,
      );
      return;
    }

    if (installed) {
      options.logger?.info(
        `Extension already installed, but it's outdated: ${installed.publisher}.${installed.name}@${installed.version}`,
      );
    }

    await shell.call("make", ["install"], {
      ...options,
      cwd: container.toString(),
    });
  },
});

type CodeExtensionManifest = {
  publisher: string;
  name: string;
  version: string;
};

class CodeExtensions {
  static async info(container: Path): Promise<CodeExtensionManifest> {
    const content = await Deno.readTextFile(
      container.join("package.json").toAbsolute().toFileUrl(),
    );
    const manifest = JSON.parse(content);

    return {
      publisher: manifest.publisher,
      name: manifest.name,
      version: manifest.version,
    };
  }

  static async list(): Promise<CodeExtensionManifest[]> {
    const result = await shell.capture(
      "code",
      ["--list-extensions", "--show-versions"],
    );

    return result.stdout
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line) => {
        const [identifier, version] = line.split("@");
        const [publisher, name] = identifier.split(".");
        return { publisher, name, version };
      });
  }

  static async find(
    nargs: { publisher: string; name: string },
  ): Promise<CodeExtensionManifest | null> {
    const extensions = await CodeExtensions.list();
    return extensions.find(
      (ext) => ext.publisher === nargs.publisher && ext.name === nargs.name,
    ) ?? null;
  }
}
