import { Command, EnumType } from "@cliffy/command";

import { Logger, LogLevel } from "@dotfiles/lib/logging.ts";
import { ConsoleFiber } from "@dotfiles/lib/io.ts";

import { ColorMode } from "./action.ts";
import * as action from "./action.ts";

// =====
// Status
// =====
type StatusOptionSet = {
  long: boolean | undefined;
  color: ColorMode;
};

const statusCommand = new Command()
  .description("Show link status")
  .type("colorMode", new EnumType(["auto", "always", "never"]))
  .option("-l, --long", "Show in long format")
  .option("--color <mode:colorMode>", "Choose colorize style", {
    default: "auto" as const,
  })
  .action((options: StatusOptionSet) => {
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
type LinkOptionSet = {
  cleanup: boolean | undefined;
  activate: boolean | undefined;
  dryRun: boolean | undefined;
  verbose: boolean | undefined;
};
const linkCommand = new Command()
  .description("Link files")
  .option("--no-cleanup", "Skip cleanup aciton before link")
  .option("--no-activate", "Skip activation after each link")
  .option("-n, --dry-run", "Do not execute commands actually")
  .option("-v, --verbose", "Show verbose messages")
  .action((options: LinkOptionSet) => {
    action.link({
      cleanup: options.cleanup ?? true,
      activate: options.activate ?? true,
      dryRun: options.dryRun ?? false,
      logger: _logger({ verbose: options.verbose ?? false }),
    });
  });

// =====
// Unlink
// =====
type UnlinkOptionSet = {
  cleanup: boolean | undefined;
  deactivate: boolean | undefined;
  dryRun: boolean | undefined;
  verbose: boolean | undefined;
};

const unlinkCommand = new Command()
  .description("Unlink files")
  .option("--no-cleanup", "Skip cleanup aciton before link")
  .option("--no-deactivate", "Skip deactivation after each link")
  .option("-n, --dry-run", "Do not execute commands actually")
  .option("-v, --verbose", "Show verbose messages")
  .action((options: UnlinkOptionSet) => {
    action.unlink({
      cleanup: options.cleanup ?? true,
      deactivate: options.deactivate ?? true,
      dryRun: options.dryRun ?? false,
      logger: _logger({ verbose: options.verbose ?? false }),
    });
  });

// =====
// Cleanup
// =====
type CleanupOptionSet = {
  dryRun: boolean | undefined;
  verbose: boolean | undefined;
};

const cleanupCommand = new Command()
  .description("Cleanup broken links")
  .option("-n, --dry-run", "Do not execute commands actually")
  .option("-v, --verbose", "Show verbose messages")
  .action((options: CleanupOptionSet) => {
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
