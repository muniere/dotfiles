import * as shell from "./shell.ts";

export type Platform = "darwin" | "default";

export async function identify(): Promise<Platform> {
  const result = await shell.capture("uname", ["-a"]);
  const name = result.stdout.trim().toLowerCase();

  if (name.includes("darwin")) {
    return "darwin";
  }
  return "default";
}
