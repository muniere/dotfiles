import { Command, EnumType } from "@cliffy/command";

import { Logger, LogLevel } from "@dotfiles/lib/logging.ts";
import { ConsoleFiber } from "@dotfiles/lib/io.ts";

import * as action from "./action.ts";

// =====
// Status
// =====
const ColorMode = new EnumType(["auto", "always", "never"]);

const statusCommand = new Command()
  .description("Show link status")
  .type("colorMode", ColorMode)
  .option("-l, --long", "Show in long format")
  .option("--color <mode:colorMode>", "Choose colorize style", {
    default: "auto" as const,
  })
  .action((options) => {
    action.status({
      long: options.long ?? false,
      color: options.color,
      fiber: ConsoleFiber.instance,
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
    .command("status", statusCommand)
    .command("link", linkCommand)
    .command("unlink", unlinkCommand)
    .command("cleanup", cleanupCommand);

  const context = await root.parse(args);

  if (!context.cmd.getParent()) {
    root.showHelp();
    Deno.exit(1);
  }
}

await main(Deno.args);
