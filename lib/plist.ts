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

  constructor(nargs: {
    path: PathLike;
  }) {
    this.path = new Path(nargs.path);
  }

  async exists(key: string): Promise<boolean> {
    const result = await this.capture(`Print "${key}"`);
    return result.status.success;
  }

  async getBoolean(key: string): Promise<boolean | null> {
    const result = await this.capture(`Print "${key}"`);
    if (result.status.success) {
      return result.stdout.trim() === "true";
    } else {
      return null;
    }
  }

  async getString(key: string): Promise<string | null> {
    const result = await this.capture(`Print "${key}"`);
    if (result.status.success) {
      return result.stdout.trim();
    } else {
      return null;
    }
  }

  async getReal(key: string): Promise<number | null> {
    const result = await this.capture(`Print "${key}"`);
    if (result.status.success) {
      return parseFloat(result.stdout.trim());
    } else {
      return null;
    }
  }

  async getArray(key: string): Promise<PropertyArray | null> {
    const result = await this.capture(`Print "${key}"`, "xml");
    if (result.status.success) {
      return plist.parse(result.stdout) as PropertyArray;
    } else {
      return null;
    }
  }

  async getDict(key: string): Promise<PropertyDict | null> {
    const result = await this.capture(`Print "${key}"`, "xml");
    if (result.status.success) {
      return plist.parse(result.stdout) as PropertyDict;
    } else {
      return null;
    }
  }

  async setBoolean(
    key: string,
    value: boolean,
    options: shell.CallOptions = {},
  ): Promise<shell.CommandStatus> {
    const hit = await this.exists(key);
    if (hit) {
      return this.call(`Set "${key}" ${value}`, options);
    } else {
      return this.call(`Add "${key}" bool ${value}`, options);
    }
  }

  async setString(
    key: string,
    value: string,
    options: shell.CallOptions = {},
  ): Promise<shell.CommandStatus> {
    const hit = await this.exists(key);
    if (hit) {
      return this.call(`Set "${key}" ${value}`, options);
    } else {
      return this.call(`Add "${key}" string "${value}"`, options);
    }
  }

  async setReal(
    key: string,
    value: number,
    options: shell.CallOptions = {},
  ): Promise<shell.CommandStatus> {
    const hit = await this.exists(key);
    if (hit) {
      return this.call(`Set "${key}" ${value}`, options);
    } else {
      return this.call(`Add "${key}" real "${value}"`, options);
    }
  }

  private call(
    command: string,
    options: shell.CallOptions = {},
  ): Promise<shell.CommandStatus> {
    const cmd = "/usr/libexec/PlistBuddy";
    const opts = ["-c", command];
    const args = this.path.toAbsolute().toString();
    return shell.call(cmd, [...opts, args], options);
  }

  private capture(
    command: string,
    format: "plist" | "xml" = "plist",
    options: shell.CaptureOptions = {},
  ): Promise<shell.CommandResult> {
    const cmd = "/usr/libexec/PlistBuddy";
    const opts = ["-c", command];

    switch (format) {
      case "plist":
        break;

      case "xml":
        opts.push("-x");
        break;
    }

    const args = this.path.toAbsolute().toString();
    return shell.capture(cmd, [...opts, args], options);
  }
}
