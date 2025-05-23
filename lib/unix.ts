import * as shell from "@dotfiles/lib/shell.ts";

export type Platform = "linux" | "darwin" | "default";

export async function identify(): Promise<Platform> {
  const result = await shell.capture("uname", ["-a"]);
  const name = result.stdout.trim().toLowerCase();

  if (name.includes("linux")) {
    return "linux";
  }
  if (name.includes("darwin")) {
    return "darwin";
  }
  return "default";
}
