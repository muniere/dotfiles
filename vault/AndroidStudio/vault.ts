import { XMLBuilder, XMLParser } from "fast-xml-parser";
import { ResLayout } from "@dotfiles/lib/layout.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";
import * as shell from "@dotfiles/lib/shell.ts";
import * as theme from "@dotfiles/lib/theme.ts";

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
  activate: async (options: shell.CallOptions) => {
    const path = ResLayout.vault().join("AndroidStudio/darwin/colors/Monokai.icls");
    const source = await Deno.readTextFile(path.toString());

    const doc = ColorSchemeDocument.parse(source);
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

class ColorSchemeDocument {
  // deno-lint-ignore no-explicit-any
  constructor(private doc: any) {}

  static parse(xml: string): ColorSchemeDocument {
    const parser = new XMLParser({
      ignoreAttributes: false,
      attributeNamePrefix: "@_",
      textNodeName: "#text",
    });
    return new ColorSchemeDocument(parser.parse(xml));
  }

  private formatColorHex(hex: string): string {
    return hex.replace("#", "").toLowerCase().replace(/^0+/, "") || "0";
  }

  /**
   * Apply default colors to options without values.
   * 
   * For example, 
   * 
   * ```xml
   * <scheme name="Monokai" version="142">
   *   <colors>
   *     <option name="BLOCK_TERMINAL_DEFAULT_FOREGROUND" value="ffffff" />
   *   </colors>
   *   <attributes>
   *     ...
   *   </attributes>
   * </scheme>
   * ``` 
   */
  applyDefaults(palette: Record<string, string>): void {
    if (!this.doc.scheme?.attributes?.option) {
      return;
    }

    const options = [this.doc.scheme.attributes.option].flat();

    for (const option of options) {
      const name = option["@_name"];
      if (!name || !palette[name]) {
        continue;
      }
      option["@_value"] = this.formatColorHex(palette[name]);
    }
  }

  /**
   * Apply colors to options with existing values.
   * 
   * For example,
   * 
   * ```xml
   * <scheme name="Monokai" version="142">
   *   <colors> 
   *   ...
   *   </colors>
   *   <attributes>
   *     <option name="BLOCK_TERMINAL_BLACK">
   *       <value>
   *         <option name="FOREGROUND" value="000000" />
   *       </value>
   *     </option>
   *   </attributes>
   * </scheme>
   * ```
   */
  applyAttributes(palette: Record<string, string>): void {
    if (!this.doc.scheme?.attributes?.option) {
      return;
    }

    const options = [this.doc.scheme.attributes.option].flat();

    for (const option of options) {
      const name = option["@_name"];
      if (!name || !palette[name] || !option.value?.option) {
        continue;
      }

      const valueOptions = [option.value.option].flat();

      for (const valueOption of valueOptions) {
        if (valueOption["@_name"] === "FOREGROUND") {
          valueOption["@_value"] = this.formatColorHex(palette[name]);
        }
      }
    }
  }

  build(options?: { trailingNewline?: boolean }): string {
    const builder = new XMLBuilder({
      ignoreAttributes: false,
      attributeNamePrefix: "@_",
      textNodeName: "#text",
      format: true,
      indentBy: "  ",
      suppressEmptyNode: true,
    });

    const xml = builder.build(this.doc).replace(/([^>\s])\/>/g, "$1 />");

    const trailingNewline = options?.trailingNewline ?? true;
    if (!trailingNewline && xml.endsWith("\n")) {
      return xml.slice(0, -1);
    }
    if (trailingNewline && !xml.endsWith("\n")) {
      return xml + "\n";
    }

    return xml;
  }
}
