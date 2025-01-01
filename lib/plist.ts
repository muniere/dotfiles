import { Path, PathLike } from "@dotfiles/lib/path.ts";
import * as plist from "plist";
import * as shell from "@dotfiles/lib/shell.ts";

export type PropertyValue = boolean | number | string | PropertyArray | PropertyDict;

export interface PropertyArray extends Array<PropertyValue> {}

export interface PropertyDict {
  [key: string]: PropertyValue;
}

export class PlistBuddy {
  private readonly path: Path;
  private readonly root: string;

  constructor(nargs: {
    path: PathLike;
    root?: string;
  }) {
    this.path = new Path(nargs.path);
    this.root = nargs.root ?? "";
  }

  async exists(key: string, options: shell.CaptureOptions = {}): Promise<boolean> {
    const entry = this.entry(key);
    const result = await this.get(entry, "raw", options);
    return result.status.success;
  }

  async getBoolean(key: string, options: shell.CaptureOptions = {}): Promise<boolean | null> {
    const entry = this.entry(key);
    const result = await this.get(entry, "raw", options);
    if (result.status.success) {
      return result.stdout.trim() === "true";
    } else {
      return null;
    }
  }

  async getString(key: string, options: shell.CaptureOptions = {}): Promise<string | null> {
    const entry = this.entry(key);
    const result = await this.get(entry, "raw", options);
    if (result.status.success) {
      return result.stdout.trim();
    } else {
      return null;
    }
  }

  async getReal(key: string, options: shell.CaptureOptions = {}): Promise<number | null> {
    const entry = this.entry(key);
    const result = await this.get(entry, "raw", options);
    if (result.status.success) {
      return parseFloat(result.stdout.trim());
    } else {
      return null;
    }
  }

  async getArray(key: string, options: shell.CaptureOptions = {}): Promise<PropertyArray | null> {
    const entry = this.entry(key);
    const result = await this.get(entry, "xml", options);
    if (result.status.success) {
      return plist.parse(result.stdout) as PropertyArray;
    } else {
      return null;
    }
  }

  async getDict(key: string, options: shell.CaptureOptions = {}): Promise<PropertyDict | null> {
    const entry = this.entry(key);
    const result = await this.get(entry, "xml", options);
    if (result.status.success) {
      return plist.parse(result.stdout) as PropertyDict;
    } else {
      return null;
    }
  }

  setBoolean(
    key: string,
    value: boolean,
    options: shell.CallOptions = {},
  ): Promise<shell.CommandStatus> {
    const entry = this.entry(key);
    return this.set(entry, "bool", value, options);
  }

  setString(
    key: string,
    value: string,
    options: shell.CallOptions = {},
  ): Promise<shell.CommandStatus> {
    const entry = this.entry(key);
    return this.set(entry, "string", value, options);
  }

  setReal(
    key: string,
    value: number,
    options: shell.CallOptions = {},
  ): Promise<shell.CommandStatus> {
    const entry = this.entry(key);
    return this.set(entry, "real", value, options);
  }

  private get(
    entry: string,
    format: "raw" | "xml" = "raw",
    options: shell.CaptureOptions = {},
  ): Promise<shell.CommandResult> {
    const cmd = "/usr/libexec/PlistBuddy";
    const opts = ["-c", `Print "${entry}"`];

    switch (format) {
      case "raw":
        break;

      case "xml":
        opts.push("-x");
        break;
    }

    const args = this.path.toAbsolute().toString();
    return shell.capture(cmd, [...opts, args], options);
  }

  private async set(
    entry: string,
    type: string,
    value: PropertyValue,
    options: shell.CallOptions = {},
  ): Promise<shell.CommandStatus> {
    const result = await this.get(entry);

    const cmd = "/usr/libexec/PlistBuddy";
    const opts = result.status.success
      ? ["-c", `Set "${entry}" ${value}`]
      : ["-c", `Add "${entry}" ${type} ${value}`];
    const args = this.path.toAbsolute().toString();
    return shell.call(cmd, [...opts, args], options);
  }

  private entry(key: string): string {
    return [this.root, key].filter((x) => x !== "").join(":");
  }
}
