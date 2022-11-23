import * as fs from "https://deno.land/std@0.163.0/fs/mod.ts";
import { Result } from "./lang.ts";

import { Lumber } from "./logging.ts";
import { Path } from "./path.ts";

// =====
// General
// =====
export type CallOptions = Pick<Deno.RunOptions, "env" | "stdout" | "stderr"> & {
  dryRun?: boolean;
  logger?: Lumber;
};

export function call(
  cmd: string[],
  options: CallOptions = {},
): Promise<Deno.ProcessStatus> {
  const env = Object.entries(options.env ?? {}).map(([k, v]) => `${k}=${v}`);
  options.logger?.trace([...env, ...cmd].join(" "));

  if (options.dryRun == true) {
    return Promise.resolve({
      success: true,
      code: 0,
    });
  }

  const proc = Deno.run({
    cmd: cmd,
    env: options.env,
    stdout: options.stdout,
    stderr: options.stderr,
  });

  return proc.status();
}

// capture does not support dry-run
export type CaptureOptions = Pick<Deno.RunOptions, "env"> & {
  logger?: Lumber;
};

export type CaptureStatus = Deno.ProcessStatus & {
  stdout: string;
  stderr: string;
};

export async function capture(
  cmd: string[],
  options: CaptureOptions = {},
): Promise<CaptureStatus> {
  options.logger?.trace(cmd.join(" "));

  const proc = Deno.run({
    cmd: cmd,
    env: options.env,
    stdout: "piped",
    stderr: "piped",
  });

  const status = await proc.status();
  const stdout = await proc.output();
  const stderr = await proc.stderrOutput();
  const decoder = new TextDecoder();

  return {
    ...status,
    stdout: decoder.decode(stdout),
    stderr: decoder.decode(stderr),
  };
}

// =====
// Short-hand
// =====
export async function which(command: string): Promise<Deno.ProcessStatus> {
  const proc = Deno.run({
    cmd: ["which", command],
    stdout: "null",
    stderr: "null",
  });

  const status = await proc.status();
  if (!status.success) {
    throw new Error();
  }

  return status;
}

export async function mkdirp(
  path: Path,
  options: CallOptions & Deno.MkdirOptions = {},
): Promise<Deno.ProcessStatus> {
  const opts = {
    recursive: options.recursive ?? true,
    mode: options.mode ?? 0o755,
  };

  const cmd = ["mkdir"]
    .concat(opts.recursive ? ["-p"] : [])
    .concat(["-m", opts.mode.toString(8)])
    .concat([path.toString()]);

  options.logger?.trace(cmd.join(" "));

  if (options.dryRun) {
    return {
      success: true,
      code: 0,
    };
  }

  try {
    await Deno.mkdir(path.toFileUrl(), opts);
    return {
      success: true,
      code: 0,
    };
  } catch {
    return {
      success: false,
      code: 1,
    };
  }
}

export async function symlink(src: Path, dst: Path, options: CallOptions = {}): Promise<Deno.ProcessStatus> {
  const cmd = ["ln"]
    .concat(["-s"])
    .concat(["-f"])
    .concat([src.toString(), dst.toString()]);

  options.logger?.trace(cmd.join(" "));

  if (options.dryRun) {
    return {
      success: true,
      code: 0,
    };
  }

  try {
    await Deno.symlink(src.toFileUrl(), dst.toFileUrl());
    return {
      success: true,
      code: 0,
    };
  } catch {
    return {
      success: false,
      code: 1,
    };
  }
}

export type CopyOptions = {
  overwrite?: boolean;
};

export async function cp(src: Path, dst: Path, options: CallOptions & CopyOptions = {}): Promise<Deno.ProcessStatus> {
  if (options.overwrite == false) {
    const stat = await Result.runAsyncOr(() => dst.stat());
    if (stat) {
      return {
        success: true,
        code: 0,
      };
    }
  }

  const cmd = ["cp", src.toString(), dst.toString()];

  options.logger?.trace(cmd.join(" "));

  if (options.dryRun) {
    return {
      success: true,
      code: 0,
    };
  }

  try {
    await Deno.copyFile(src.toFileUrl(), dst.toFileUrl());
    return {
      success: true,
      code: 0,
    };
  } catch {
    return {
      success: false,
      code: 1,
    };
  }
}

export async function rm(path: Path, options: CallOptions = {}): Promise<Deno.ProcessStatus> {
  const cmd = ["rm"]
    .concat(["-f"])
    .concat([path.toString()]);

  options.logger?.trace(cmd.join(" "));

  if (options.dryRun) {
    return {
      success: true,
      code: 0,
    };
  }

  await Deno.remove(path.toFileUrl()).catch((_) => {});
  return {
    success: true,
    code: 0,
  };
}

export async function touch(path: Path, options: CallOptions = {}): Promise<Deno.ProcessStatus> {
  options.logger?.trace(`touch ${path}`);

  if (options.dryRun) {
    return {
      success: true,
      code: 0,
    };
  }

  try {
    await fs.ensureFile(path.toFileUrl());
    return {
      success: true,
      code: 0,
    };
  } catch {
    return {
      success: false,
      code: 1,
    };
  }
}

export type CurlOptions = {
  fail?: boolean;
  showError?: boolean;
  location?: boolean;
  output?: Path | URL | string;
};

export function curl(url: URL | string, options: CallOptions & CurlOptions = {}): Promise<Deno.ProcessStatus> {
  return call(
    ["curl"]
      .concat(options.fail != false ? ["-f"] : [])
      .concat(options.showError != false ? ["-S"] : [])
      .concat(options.location != false ? ["-L"] : [])
      .concat(options.output ? ["--create-dirs", "-o", options.output.toString()] : [])
      .concat(url.toString()),
    options,
  );
}
