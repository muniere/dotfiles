import { Command, CompletionsCommand, EnumType } from "https://deno.land/x/cliffy@v0.25.4/command/mod.ts";

import { Logger, LogLevel } from "./logging.ts";

import * as action from "./action.ts";

// =====
// List
// =====
const ColorMode = new EnumType(["auto", "always", "never"]);

const listCommand = new Command()
  .description("List links")
  .type("colorMode", ColorMode)
  .option("-l, --long", "Show in long format")
  .option("--color <mode:colorMode>", "Choose colorize style", {
    default: "auto" as const,
  })
  .action((options) => {
    action.list({
      long: options.long ?? false,
      color: options.color,
      stream: Deno.stdout,
      logger: _logger(),
    });
  });

// =====
// Link
// =====
const linkCommand = new Command()
  .description("Link files")
  .option("--no-cleanup", "Skip cleanup aciton before link")
  .option("--no-activate", "Skip activation after each link")
  .option("-n, --dry-run", "Do not execute commands actually")
  .option("-v, --verbose", "Show verbose messages")
  .action((options) => {
    action.link({
      cleanup: options.cleanup,
      activate: options.activate,
      dryRun: options.dryRun ?? false,
      logger: _logger({ verbose: options.verbose ?? false }),
    });
  });

// =====
// Unlink
// =====
const unlinkCommand = new Command()
  .description("Unlink files")
  .option("--no-cleanup", "Skip cleanup aciton before link")
  .option("--no-deactivate", "Skip deactivation after each link")
  .option("-n, --dry-run", "Do not execute commands actually")
  .option("-v, --verbose", "Show verbose messages")
  .action((options) => {
    action.unlink({
      cleanup: options.cleanup,
      deactivate: options.deactivate,
      dryRun: options.dryRun ?? false,
      logger: _logger({ verbose: options.verbose ?? false }),
    });
  });

// =====
// Cleanup
// =====
const cleanupCommand = new Command()
  .description("Cleanup broken links")
  .option("-n, --dry-run", "Do not execute commands actually")
  .option("-v, --verbose", "Show verbose messages")
  .action((options) => {
    action.cleanup({
      dryRun: options.dryRun ?? false,
      logger: _logger({ verbose: options.verbose ?? false }),
    });
  });

// =====
// Completion
// =====
const completionCommand = new CompletionsCommand();

// =====
// Shared
// =====
function _logger(options: { verbose?: boolean } = {}): Logger {
  return new Logger({
    level: options.verbose == true ? LogLevel.DEBUG : LogLevel.TRACE,
  });
}

// =====
// Main
// =====
async function main(args: string[]) {
  const root = new Command()
    .name("xake")
    .command("list", listCommand)
    .command("link", linkCommand)
    .command("unlink", unlinkCommand)
    .command("cleanup", cleanupCommand)
    .command("completion", completionCommand);

  const context = await root.parse(args);

  if (!context.cmd.getParent()) {
    root.showHelp();
    Deno.exit(1);
  }
}

await main(Deno.args);
