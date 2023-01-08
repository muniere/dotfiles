import { Logger } from "./logging.ts";
import { Path } from "./path.ts";

const decoder = new TextDecoder();

export type ProcessStatus = Deno.ProcessStatus;

export type ProcessResult = {
  status: ProcessStatus;
  stdout: string;
  stderr: string;
};

// =====
// General
// =====
export type CallOptions =
  & Pick<Deno.RunOptions, "cwd" | "env" | "stdout" | "stderr">
  & {
    dryRun?: boolean;
    logger?: Logger;
  };

export function call(
  cmd: string[],
  options: CallOptions = {},
): Promise<ProcessStatus> {
  const cd = options.cwd ? ["cd", options.cwd, "&&"] : [];
  const env = Object.entries(options.env ?? {}).map(([k, v]) => `${k}=${v}`);
  options.logger?.trace([...cd, ...env, ...cmd].join(" "));

  if (options.dryRun == true) {
    return Promise.resolve({
      success: true,
      code: 0,
    });
  }

  const proc = Deno.run({
    cmd: cmd,
    cwd: options.cwd,
    env: options.env,
    stdout: options.stdout,
    stderr: options.stderr,
  });

  return proc.status();
}

export type CaptureOptions =
  & Pick<Deno.RunOptions, "cwd" | "env">
  & {
    logger?: Logger;
  };

export async function capture(
  cmd: string[],
  options: CaptureOptions = {},
): Promise<ProcessResult> {
  const cd = options.cwd ? ["cd", options.cwd, "&&"] : [];
  const env = Object.entries(options.env ?? {}).map(([k, v]) => `${k}=${v}`);
  options.logger?.trace([...cd, ...env, ...cmd].join(" "));

  const proc = Deno.run({
    cmd: cmd,
    cwd: options.cwd,
    env: options.env,
    stdout: "piped",
    stderr: "piped",
  });

  const status = await proc.status();
  const stdout = await proc.output().then((data) => decoder.decode(data));
  const stderr = await proc.stderrOutput().then((data) => decoder.decode(data));

  return { status, stdout, stderr };
}

// =====
// Short-hand
// =====
export function mkdir(
  path: Path,
  options: CallOptions & Deno.MkdirOptions = {},
): Promise<ProcessStatus> {
  return call(
    [
      "mkdir",
      ...((options.recursive ?? true) ? ["-p"] : []),
      ...(options.mode ? ["-m", options.mode.toString(8)] : []),
      path.toString(),
    ],
    options,
  );
}

export function symlink(
  src: Path,
  dst: Path,
  options: CallOptions = {},
): Promise<Deno.ProcessStatus> {
  return call(["ln", "-s", "-f", src.toString(), dst.toString()], options);
}

export type CopyOptions = {
  overwrite?: boolean;
};

export function cp(
  src: Path,
  dst: Path,
  options: CallOptions & CopyOptions = {},
): Promise<Deno.ProcessStatus> {
  return call(
    [
      "cp",
      ...((options.overwrite ?? false) ? ["-n"] : []),
      src.toString(),
      dst.toString(),
    ],
    options,
  );
}

export function rm(
  path: Path,
  options: CallOptions = {},
): Promise<Deno.ProcessStatus> {
  return call(["rm", "-r", path.toString()], options);
}

export function touch(
  path: Path,
  options: CallOptions = {},
): Promise<Deno.ProcessStatus> {
  return call(["touch", path.toString()], options);
}

export type CurlOptions = {
  fail?: boolean;
  showError?: boolean;
  location?: boolean;
  output?: Path | URL | string;
};

export function curl(
  url: URL | string,
  options: CallOptions & CurlOptions = {},
): Promise<ProcessStatus> {
  return call(
    [
      "curl",
      ...((options.fail ?? true) ? ["-f"] : []),
      ...((options.showError ?? true) ? ["-S"] : []),
      ...((options.location ?? true) ? ["-L"] : []),
      ...(options.output ? ["--create-dirs"] : []),
      ...(options.output ? ["-o", options.output.toString()] : []),
      url.toString(),
    ],
    options,
  );
}
