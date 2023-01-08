import { Path, PathLike } from "./path.ts";
import * as shell from "./shell.ts";

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

  async setBoolean(
    key: string,
    value: boolean,
    options: shell.CallOptions = {},
  ): Promise<shell.ProcessStatus> {
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
  ): Promise<shell.ProcessStatus> {
    const hit = await this.exists(key);
    if (hit) {
      return this.call(`Set "${key}" ${value}`, options);
    } else {
      return this.call(`Add "${key}" string "${value}"`, options);
    }
  }

  private call(
    command: string,
    options: shell.CallOptions = {},
  ): Promise<shell.ProcessStatus> {
    return shell.call([
      "/usr/libexec/PlistBuddy",
      "-c",
      command,
      this.path.toAbsolute().toString(),
    ], options);
  }

  private capture(
    command: string,
    options: shell.CaptureOptions = {},
  ): Promise<shell.ProcessResult> {
    return shell.capture([
      "/usr/libexec/PlistBuddy",
      "-c",
      command,
      this.path.toAbsolute().toString(),
    ], options);
  }
}
