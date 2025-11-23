import { XMLBuilder, XMLParser } from "fast-xml-parser";

/**
 * Represents a JetBrains IDE color scheme document.
 *
 * This class provides utilities for parsing, modifying, and building
 * color scheme files (.icls) used by JetBrains IDEs such as IntelliJ IDEA,
 * Android Studio, PyCharm, etc.
 */
export class IdeaColorSchemeDocument {
  // deno-lint-ignore no-explicit-any
  constructor(private doc: any) {}

  /**
   * Parses an XML string into a IdeaColorSchemeDocument.
   *
   * @param xml - The XML content of the color scheme file
   * @returns A new IdeaColorSchemeDocument instance
   */
  static parse(xml: string): IdeaColorSchemeDocument {
    const parser = new XMLParser({
      ignoreAttributes: false,
      attributeNamePrefix: "@_",
      textNodeName: "#text",
    });
    return new IdeaColorSchemeDocument(parser.parse(xml));
  }

  private formatColorHex(hex: string): string {
    return hex.replace("#", "").toLowerCase().replace(/^0+/, "") || "0";
  }

  /**
   * Applies default colors to color options.
   *
   * This method updates the `value` attributes of `<option>` elements within
   * the `<colors>` section of the color scheme.
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
   *
   * @param palette - A mapping of option names to color hex values
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
   * Applies colors to attribute options.
   *
   * This method updates the `FOREGROUND` color within nested `<option>` elements
   * in the `<attributes>` section of the color scheme.
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
   *
   * @param palette - A mapping of attribute names to color hex values
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
