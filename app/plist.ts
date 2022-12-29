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
    const options: shell.CallOptions = {
      stdout: "piped",
      stderr: "piped",
    };

    const result = await this.run(`Print "${key}"`, options);
    return result.success;
  }

  async setBoolean(
    key: string,
    value: boolean,
    options: shell.CallOptions = {},
  ): Promise<Deno.ProcessStatus> {
    const hit = await this.exists(key);
    if (hit) {
      return this.run(`Set "${key}" ${value}`, options);
    } else {
      return this.run(`Add "${key}" bool ${value}`, options);
    }
  }

  async setString(
    key: string,
    value: string,
    options: shell.CallOptions = {},
  ): Promise<Deno.ProcessStatus> {
    const hit = await this.exists(key);
    if (hit) {
      return this.run(`Set "${key}" ${value}`, options);
    } else {
      return this.run(`Add "${key}" string "${value}"`, options);
    }
  }

  private run(command: string, options: shell.CallOptions = {}): Promise<Deno.ProcessStatus> {
    return shell.call([
      "/usr/libexec/PlistBuddy",
      "-c",
      command,
      this.path.toAbsolute().toString(),
    ], options);
  }
}
