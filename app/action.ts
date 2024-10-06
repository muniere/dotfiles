import { sprintf } from "stdlib/fmt/printf.ts";
import * as colors from "stdlib/fmt/colors.ts";
import { Eta } from "eta/src/index.ts";

import { Fiber } from "../lib/io.ts";
import { Pipeline, Result, run } from "../lib/lang.ts";
import { Logger } from "../lib/logging.ts";
import { Path, PathFilter } from "../lib/path.ts";
import {
  ChainBase,
  CookBook,
  PrefChain,
  PrefSpec,
  SpecBase,
  TmplChain,
  TmplSpec,
} from "../lib/schema.ts";

import * as shell from "../lib/shell.ts";
import * as unix from "../lib/unix.ts";

import { ResLayout } from "./layout.ts";

import * as vault from "./vault.ts";

// =====
// Shared
// =====
abstract class Action<Context> {
  constructor(
    protected readonly context: Context,
  ) {}

  abstract run(): Promise<void>;

  private static readonly filter = PathFilter.blacklist([
    "**/*.swp",
    "**/*.bak",
    "**/.DS_Store",
    "**/.keep",
    "**/.gitkeep",
  ]);

  protected books(
    options: {
      platform?: unix.Platform;
    } = {},
  ): CookBook[] {
    const books = [
      vault.HomeCookBook,
      vault.LibraryCookBook,
      vault.BinCookBook,
      vault.ShCookBook,
      vault.BashCookBook,
      vault.ZshCookBook,
      vault.ZshSiteFunctionsCookBook,
      vault.VimCookBook,
      vault.NeovimCookBook,
      vault.GitCookBook,
      vault.TigCookBook,
      vault.GitHubCookBook,
      vault.DockerCookBook,
      vault.AsdfCookBook,
      vault.YaziCookBook,
      vault.TmuxCookBook,
      vault.GradleCookBook,
      vault.PythonCookBook,
      vault.NodeCookBook,
      vault.iTermCookBook,
      vault.XcodeCookBook,
      vault.IntelliJCookBook,
      vault.AndroidStudioCookBook,
    ];

    const platform = options.platform;
    if (!platform) {
      return books;
    }

    return books.filter((book) => book.supports(platform));
  }

  protected inflatePrefSpecSync(
    spec: PrefSpec,
    options: {
      container?: Path;
      platform?: unix.Platform;
    } = {},
  ): PrefChain[] {
    if (spec.src.isAbsolute) {
      return this.travarseSync(spec);
    }

    const container = options.container ?? ResLayout.pref();
    const platform = options.platform ?? "default";
    const layout = spec.options?.layout ?? "by-platform";

    switch (layout) {
      case "by-platform":
        switch (platform) {
          case "default":
            return this.travarseSync(spec, {
              prefix: container.join("default"),
            });

          case "darwin":
            return [
              ...this.travarseSync(spec, {
                prefix: container.join(platform),
              }),
              ...this.travarseSync(spec, {
                prefix: container.join("default"),
              }),
            ];
        }
        break;

      case "by-component":
        switch (platform) {
          case "default":
            return this.travarseSync(spec, {
              prefix: container,
              suffix: new Path(platform),
            });
          case "darwin":
            return [
              ...this.travarseSync(spec, {
                prefix: container,
                suffix: new Path(platform),
              }),
              ...this.travarseSync(spec, {
                prefix: container,
                suffix: new Path("default"),
              }),
            ];
        }
        break;
    }

    return [];
  }

  protected inflateTmplSpecSync(
    spec: TmplSpec,
  ): TmplChain[] {
    if (spec.src.isAbsolute) {
      return this.travarseSync(spec);
    } else {
      return this.travarseSync(spec, { prefix: ResLayout.tmpl() });
    }
  }

  protected travarseSync<Chain extends ChainBase>(
    spec: SpecBase<Chain>,
    options: {
      prefix?: Path;
      suffix?: Path;
    } = {},
  ): Chain[] {
    const prefix = options.prefix ?? new Path();
    const suffix = options.suffix ?? new Path();

    const src = run(() => {
      if (spec.src.isAbsolute) {
        return new Path(spec.src.expandHome());
      } else {
        return new Path(prefix, spec.src.expandHome(), suffix).toAbsolute();
      }
    });

    const dst = spec.dst.expandHome().toAbsolute();

    const stat = Result.run(() => src.lstatSync()).value;

    if (!stat) {
      return [];
    }

    if (stat.isFile) {
      return [
        spec.chain({
          src: src,
          dst: dst,
        }),
      ];
    }

    return [...src.walkSync()]
      .filter((entry) => entry.isFile)
      .map((entry) => new Path(entry.path))
      .map((path) =>
        spec.chain({
          src: path,
          dst: new Path(dst, path.relative(src)),
        })
      );
  }

  protected test(path: Path): boolean {
    return Action.filter.test(path);
  }
}

// =====
// Status
// =====
export function status(context: StatusContext): Promise<void> {
  return new StatusAction(context).run();
}

export type ColorMode = "auto" | "always" | "never";

export type StatusContext = {
  long: boolean;
  color: ColorMode;
  fiber: Fiber;
  logger?: Logger;
};

class StatusAction extends Action<StatusContext> {
  private get colored(): boolean {
    switch (this.context.color) {
      case "always":
        return true;
      case "never":
        return false;
      case "auto":
        return this.context.fiber.isTerminal();
    }
    return false;
  }

  override async run(): Promise<void> {
    const platform = await unix.identify();
    const encoder = new TextEncoder();

    // pref
    {
      const chains = this.inflatePrefChainSync({ platform: platform });

      const header = Pipeline.perform(
        "[[ Preferences ]]",
        colors.yellow,
        colors.bold,
      );

      const lines = chains
        .filter((chain) => this.test(chain.src))
        .toSorted((a, b) => a.dst < b.dst ? -1 : 1)
        .map((chain) => this.format(chain, { separator: " -> " }));

      const bytes = encoder.encode([header, ...lines].join("\n") + "\n");

      await this.context.fiber.writeAll(bytes);
    }

    await this.context.fiber.writeAll(encoder.encode("\n"));

    // tmpl
    {
      const chains = this.inflateTmplChainSync({ platform: platform });

      const header = Pipeline.perform(
        "[[ Templates ]]",
        colors.yellow,
        colors.bold,
      );

      const lines = chains
        .filter((chain) => this.test(chain.src))
        .toSorted((a, b) => a.dst < b.dst ? -1 : 1)
        .map((chain) => this.format(chain, { separator: " <- " }));

      const bytes = encoder.encode([header, ...lines].join("\n") + "\n");

      await this.context.fiber.writeAll(bytes);
    }
  }

  private inflatePrefChainSync(
    options: {
      platform?: unix.Platform;
    } = {},
  ): PrefChain[] {
    return this.books(options).flatMap((book) => {
      return book.prefs.flatMap((pref) => {
        return this.inflatePrefSpecSync(pref, {
          container: book.container,
          platform: options.platform,
        });
      });
    });
  }

  private inflateTmplChainSync(
    options: {
      container?: Path;
      platform?: unix.Platform;
    } = {},
  ): TmplChain[] {
    return this.books(options).flatMap((book) => {
      return book.tmpls.flatMap((tmpl) => {
        return this.inflateTmplSpecSync(tmpl);
      });
    });
  }

  private format(chain: ChainBase, options: { separator: string }): string {
    const decorate = this.colored
      ? Result.run(() => chain.dst.lstatSync()).fold({
        onSuccess: (stat) => this.decoration(stat),
        onFailure: (_) => Pipeline.of(colors.red),
      })
      : undefined;

    const dst = run(() => {
      if (decorate) {
        return decorate.perform(chain.dst.toString());
      } else {
        return chain.dst.toString();
      }
    });

    const src = chain.src.toString();

    switch (this.context.long) {
      case true:
        return [dst, src].join(options.separator);

      case false:
        return dst;
    }
  }

  private decoration(stat: Deno.FileInfo): Pipeline<string> {
    if (stat.isSymlink) {
      return Pipeline.of(colors.magenta);
    }
    if (stat.isDirectory) {
      return Pipeline.of(colors.blue);
    }
    if (stat.isFile) {
      return Pipeline.of(colors.reset);
    }
    return Pipeline.of(colors.reset);
  }
}

// =====
// Link
// =====
export function link(context: LinkContext): Promise<void> {
  return new LinkAction(context).run();
}

export type LinkContext = {
  cleanup: boolean;
  activate: boolean;
  dryRun: boolean;
  logger?: Logger;
};

class LinkAction extends Action<LinkContext> {
  private get shellOptions(): shell.CallOptions {
    return {
      dryRun: this.context.dryRun,
      logger: this.context.logger,
    };
  }

  override async run(): Promise<void> {
    const platform = await unix.identify();

    const books = this.books({ platform: platform });

    if (this.context.cleanup) {
      await this.cleanup(books);
    }

    for (const [i, book] of books.entries()) {
      const format = "(%02d/%02d) %s Launched";
      const message = sprintf(format, i + 1, books.length, book.name);
      this.context.logger?.mark(message, { bold: true });

      for (const spec of book.prefs) {
        await this.linkPref(spec, {
          container: book.container,
          platform: platform,
        });
      }
      if (this.context.activate) {
        await this.activate(book);
      }
      for (const spec of book.tmpls) {
        await this.forgeTmpl(spec);
      }
    }
  }

  private cleanup(books: CookBook[]): Promise<void> {
    const action = new CleanupAction(this.context);
    return action.perform(books);
  }

  private async linkPref(
    spec: PrefSpec,
    options: {
      container?: Path;
      platform?: unix.Platform;
    } = {},
  ): Promise<void> {
    const chains = this.inflatePrefSpecSync(spec, options);

    for (const chain of chains) {
      if (!this.test(chain.src)) {
        this.context.logger?.debug(`File ignored: ${chain.src}`);
        continue;
      }
      const srcStat = await Result.runAsyncOr(() => chain.src.lstat());
      if (!srcStat) {
        this.context.logger?.info(`File not found: ${chain.src}`);
        continue;
      }
      const dstStat = await Result.runAsyncOr(() => chain.dst.lstat());
      if (dstStat && dstStat.isSymlink) {
        this.context.logger?.info(`Symlink already exists: ${chain.dst}`);
        continue;
      }
      if (dstStat && dstStat.isFile) {
        this.context.logger?.info(`File already exists: ${chain.dst}`);
        continue;
      }

      const dir = chain.dst.dirname();
      const dirStat = await Result.runAsyncOr(() => dir.lstat());
      if (!dirStat) {
        await shell.mkdir(dir, this.shellOptions);
      }

      switch (chain.options?.kind ?? "link") {
        case "link":
          await shell.symlink(chain.src, chain.dst, this.shellOptions);
          break;
        case "copy":
          await shell.cp(chain.src, chain.dst, this.shellOptions);
          break;
      }
    }
  }

  private async forgeTmpl(spec: TmplSpec): Promise<void> {
    const chains = this.inflateTmplSpecSync(spec);

    for (const chain of chains) {
      const dstStat = await Result.runAsyncOr(() => chain.dst.stat());
      if (dstStat && dstStat.isFile) {
        this.context.logger?.info(`File already created: ${chain.dst}`);
        return;
      }

      const template = await Deno.readTextFile(chain.src.toFileUrl());
      const values = chain.options?.values ?? {};
      const content = new Eta().renderString(template, values);

      const dirStat = await Result.runAsyncOr(() => chain.dst.dirname().stat());
      if (!dirStat) {
        await shell.mkdir(chain.dst.dirname(), this.shellOptions);
      }

      this.context.logger?.info(
        `Create a file ${chain.dst} with content:\n${content.trimEnd()}`,
      );

      if (this.shellOptions.dryRun == true) {
        return;
      }

      await Deno.writeTextFile(chain.dst.toFileUrl(), content);
    }
  }

  private async activate(book: CookBook): Promise<void> {
    await book.activate(this.shellOptions);
  }
}

// =====
// Unlink
// =====
export function unlink(context: UnlinkContext): Promise<void> {
  return new UnlinkAction(context).run();
}

export type UnlinkContext = {
  cleanup: boolean;
  deactivate: boolean;
  dryRun: boolean;
  logger?: Logger;
};

class UnlinkAction extends Action<UnlinkContext> {
  private get shellOptions(): shell.CallOptions {
    return {
      dryRun: this.context.dryRun,
      logger: this.context.logger,
    };
  }

  override async run(): Promise<void> {
    const platform = await unix.identify();

    const books = this.books({ platform: platform }).toReversed();

    if (this.context.cleanup) {
      await this.cleanup(books);
    }

    for (const [i, book] of books.entries()) {
      const format = "(%02d/%02d) %s Launched";
      const message = sprintf(format, i + 1, books.length, book.name);
      this.context.logger?.mark(message, { bold: true });

      for (const spec of book.tmpls) {
        await this.recallTmpl(spec);
      }
      if (this.context.deactivate) {
        await this.deactivate(book);
      }
      for (const spec of book.prefs) {
        await this.unlinkPref(spec, {
          container: book.container,
          platform: platform,
        });
      }
    }
  }

  private cleanup(books: CookBook[]): Promise<void> {
    const action = new CleanupAction(this.context);
    return action.perform(books);
  }

  private async unlinkPref(
    spec: PrefSpec,
    options: {
      container?: Path;
      platform?: unix.Platform;
    } = {},
  ): Promise<void> {
    const chains = this.inflatePrefSpecSync(spec, options);

    for (const chain of chains) {
      if (!this.test(chain.src)) {
        this.context.logger?.debug(`File ignored: ${chain.src}`);
        continue;
      }
      const srcStat = await Result.runAsyncOr(() => chain.src.lstat());
      if (!srcStat) {
        this.context.logger?.info(`File not found: ${chain.src}`);
        continue;
      }
      const dstStat = await Result.runAsyncOr(() => chain.dst.lstat());
      if (!dstStat) {
        this.context.logger?.info(`File already removed: ${chain.dst}`);
        continue;
      }
      if (dstStat.isFile) {
        this.context.logger?.info(`File is normal file: ${chain.dst}`);
        continue;
      }

      await shell.rm(chain.dst, this.shellOptions);
    }
  }

  private async recallTmpl(spec: TmplSpec): Promise<void> {
    const chains = this.inflateTmplSpecSync(spec);

    for (const chain of chains) {
      const stat = await Result.runAsyncOr(() => chain.dst.stat());
      if (!stat) {
        this.context.logger?.info(`File not found: ${chain.dst}`);
        return;
      }
      if (!stat.isFile) {
        this.context.logger?.info(`File is not normal file: ${chain.dst}`);
        return;
      }

      await shell.rm(chain.dst, this.shellOptions);
    }
  }

  private async deactivate(book: CookBook): Promise<void> {
    await book.deactivate(this.shellOptions);
  }
}

// =====
// Cleanup
// ====
export function cleanup(context: CleanupContext): Promise<void> {
  return new CleanupAction(context).run();
}
export type CleanupContext = {
  dryRun: boolean;
  logger?: Logger;
};

class CleanupAction extends Action<CleanupContext> {
  private get shellOptions(): shell.CallOptions {
    return {
      dryRun: this.context.dryRun,
      logger: this.context.logger,
    };
  }

  override async run(): Promise<void> {
    const platform = await unix.identify();

    const books = this.books({ platform: platform });

    return this.perform(books, { force: true });
  }

  async perform(
    books: CookBook[],
    options: { force?: boolean } = {},
  ): Promise<void> {
    const banner = "Scanning broken symlinks";
    this.context.logger?.info(`${banner}...\r`, { term: false });

    const specs = books
      .flatMap((book) => book.prefs)
      .toSorted((a, b) => a.dst.expandHome() < b.dst.expandHome() ? -1 : 1);

    const found: Path[] = [];
    for (const spec of specs) {
      const path = spec.dst.expandHome();

      if (spec.options?.autoclean == false && options.force != true) {
        this.context.logger?.debug(`Skipping ${path}`);
        continue;
      }

      const message = `Scanning ${path}`;
      this.context.logger?.debug(`${message}...\r`, { term: false });
      found.push(...this.traverseSync(path));
      this.context.logger?.debug(`${message}... Done`);
    }

    this.context.logger?.info(`${banner}... Done`);

    if (found.length > 0) {
      this.context.logger?.info(`Found ${found.length} broken symlinks`);
    } else {
      this.context.logger?.info(`No broken symlinks were found`);
    }

    for (const path of found) {
      await shell.rm(path, this.shellOptions);
    }
  }

  private traverseSync(path: Path): Path[] {
    const lstat = Result.runOr(() => path.lstatSync());
    if (!lstat) {
      return [];
    }
    if (lstat.isSymlink) {
      if (!Result.runOr(() => path.statSync())) {
        return [path];
      }
      return [];
    }
    if (lstat.isFile) {
      return [];
    }
    if (lstat.isDirectory) {
      return [...path.walkSync()]
        .filter((entry) => entry.isSymlink)
        .map((entry) => new Path(entry.path))
        .filter((path) => !Result.runOr(() => path.statSync()));
    }
    return [];
  }
}
