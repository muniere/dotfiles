import { Logger } from "./logging.ts";
import { Path } from "./path.ts";

const decoder = new TextDecoder();

export type CommandStatus = Deno.CommandStatus;

export type CommandResult = {
  status: CommandStatus;
  stdout: string;
  stderr: string;
};

// =====
// General
// =====
export type CallOptions =
  & Pick<Deno.CommandOptions, "cwd" | "env" | "stdout" | "stderr">
  & {
    dryRun?: boolean;
    logger?: Logger;
  };

export function call(
  cmd: string,
  args?: string[],
  options: CallOptions = {},
): Promise<CommandStatus> {
  const cd = options.cwd ? ["cd", options.cwd, "&&"] : [];
  const env = Object.entries(options.env ?? {}).map(([k, v]) => `${k}=${v}`);
  options.logger?.trace([...cd, ...env, cmd, ...(args ?? [])].join(" "));

  if (options.dryRun == true) {
    return Promise.resolve({
      success: true,
      code: 0,
      signal: null,
    });
  }

  const command = new Deno.Command(cmd, {
    args: args,
    cwd: options.cwd,
    env: options.env,
    stdout: options.stdout,
    stderr: options.stderr,
  });

  return command.spawn().status;
}

export type CaptureOptions =
  & Pick<Deno.CommandOptions, "cwd" | "env">
  & {
    logger?: Logger;
  };

export async function capture(
  cmd: string,
  args?: string[],
  options: CaptureOptions = {},
): Promise<CommandResult> {
  const cd = options.cwd ? ["cd", options.cwd, "&&"] : [];
  const env = Object.entries(options.env ?? {}).map(([k, v]) => `${k}=${v}`);
  options.logger?.trace([...cd, ...env, cmd, ...(args ?? [])].join(" "));

  const command = new Deno.Command(cmd, {
    args: args,
    cwd: options.cwd,
    env: options.env,
    stdout: "piped",
    stderr: "piped",
  });

  const { code, success, signal, stdout, stderr } = await command.output();

  return {
    status: { code, success, signal },
    stdout: decoder.decode(stdout),
    stderr: decoder.decode(stderr),
  };
}

// =====
// Short-hand
// =====
export type MkdirOptions = CallOptions & Deno.MkdirOptions;

export function mkdir(
  path: Path,
  options: MkdirOptions,
): Promise<CommandStatus> {
  const cmd = "mkdir";
  const opts = [
    ...((options.recursive ?? true) ? ["-p"] : []),
    ...(options.mode ? ["-m", options.mode.toString(8)] : []),
  ];
  const args = [
    path.toString(),
  ];
  return call(cmd, [...opts, ...args], options);
}

export type SymlinkOptions = CallOptions;

export function symlink(
  src: Path,
  dst: Path,
  options: SymlinkOptions = {},
): Promise<CommandStatus> {
  const cmd = "ln";
  const opts = ["-s", "-f"];
  const args = [
    src.toString(),
    dst.toString(),
  ];
  return call(cmd, [...opts, ...args], options);
}

export type CopyOptions = CallOptions & {
  overwrite?: boolean;
};

export function cp(
  src: Path,
  dst: Path,
  options: CopyOptions = {},
): Promise<CommandStatus> {
  const cmd = "cp";
  const opts = [
    ...((options.overwrite ?? false) ? ["-n"] : []),
  ];
  const args = [
    src.toString(),
    dst.toString(),
  ];
  return call(cmd, [...opts, ...args], options);
}

export type RmOptions = CallOptions;

export function rm(
  path: Path,
  options: RmOptions = {},
): Promise<CommandStatus> {
  const cmd = "rm";
  const opts = ["-r"];
  const args = [path.toString()];
  return call(cmd, [...opts, ...args], options);
}

export type TouchOptions = CallOptions;

export function touch(
  path: Path,
  options: TouchOptions = {},
): Promise<CommandStatus> {
  const cmd = "touch";
  const args = [path.toString()];
  return call(cmd, args, options);
}

export type CurlOptions = CallOptions & {
  fail?: boolean;
  showError?: boolean;
  location?: boolean;
  output?: Path | URL | string;
};

export function curl(
  url: URL | string,
  options: CurlOptions = {},
): Promise<CommandStatus> {
  const cmd = "curl";
  const opts = [
    ...((options.fail ?? true) ? ["-f"] : []),
    ...((options.showError ?? true) ? ["-S"] : []),
    ...((options.location ?? true) ? ["-L"] : []),
    ...(options.output ? ["--create-dirs"] : []),
    ...(options.output ? ["-o", options.output.toString()] : []),
  ];
  const args = [
    url.toString(),
  ];
  return call(cmd, [...opts, ...args], options);
}
