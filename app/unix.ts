export type Platform = "darwin" | "default";

const decoder = new TextDecoder();

export async function identify(): Promise<Platform> {
  const output = await Deno.run({
    cmd: ["uname", "-a"],
    stdout: "piped",
    stderr: "piped",
  }).output();

  const name = decoder.decode(output).trim().toLowerCase();

  if (name.includes("darwin")) {
    return "darwin";
  }
  return "default";
}
