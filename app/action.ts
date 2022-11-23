import { sprintf } from "https://deno.land/std@0.163.0/fmt/printf.ts";
import * as streams from "https://deno.land/std@0.163.0/streams/mod.ts";

import { Result, run } from "./lang.ts";
import { ResLayout } from "./layout.ts";
import { LogStream, Lumber } from "./logging.ts";
import { Path, PathFilter } from "./path.ts";
import { ChainBase, CookBook, PrefChain, PrefRecipe, RecipeBase, SnipRecipe } from "./schema.ts";
import { Color } from "./tty.ts";

import * as shell from "./shell.ts";
import * as unix from "./unix.ts";
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

  protected books(options: { platform?: unix.Platform } = {}): CookBook[] {
    const books = [
      vault.HomeCookBook,
      vault.LibraryCookBook,
      vault.BinCookBook,
      vault.ShCookBook,
      vault.BashCookBook,
      vault.ZshCookBook,
      vault.VimCookBook,
      vault.GitCookBook,
      vault.GitHubCookBook,
      vault.AsdfCookBook,
      vault.TmuxCookBook,
      vault.GradleCookBook,
      vault.PythonCookBook,
      vault.RubyCookBook,
      vault.NodeCookBook,
      vault.XcodeCookBook,
      vault.IntelliJCookBook,
      vault.AndroidStudioCookBook,
      vault.AppCodeCookBook,
      vault.RubyMineCookBook,
      vault.GoLandCookBook,
      vault.RiderCookBook,
    ];

    const platform = options.platform;
    if (!platform) {
      return books;
    }

    return books.filter((book) => book.supports(platform));
  }

  protected travarseSync<Chain extends ChainBase>(
    recipe: RecipeBase<Chain>,
    options: { prefix?: Path } = {},
  ): Chain[] {
    const src = recipe.src.isAbsolute
      ? new Path(recipe.src.expandHome())
      : new Path(options.prefix ?? new Path(), recipe.src.expandHome()).toAbsolute();

    const dst = recipe.dst.expandHome().toAbsolute();

    const stat = Result.run(() => src.lstatSync()).value;

    if (!stat) {
      return [];
    }

    if (stat.isFile) {
      return [
        recipe.chain({
          src: src,
          dst: dst,
        }),
      ];
    }

    return [...src.walkSync()]
      .filter((entry) => entry.isFile)
      .map((entry) => new Path(entry.path))
      .map((path) =>
        recipe.chain({
          src: path,
          dst: new Path(dst, path.relative(src)),
        })
      );
  }

  protected allows(path: Path): boolean {
    return Action.filter.allow(path);
  }
}

// =====
// List
// =====
export function list(context: ListContext): Promise<void> {
  return new ListAction(context).run();
}

export type ColorMode = "auto" | "always" | "never";

export type ListContext = {
  long: boolean;
  color: ColorMode;
  stream: LogStream;
  logger?: Lumber;
};

class ListAction extends Action<ListContext> {
  private get colored(): boolean {
    switch (this.context.color) {
      case "always":
        return true;
      case "never":
        return false;
      case "auto":
        return Deno.isatty(this.context.stream.rid);
    }
    return false;
  }

  override async run(): Promise<void> {
    const platform = await unix.identify();

    const recipes = this.books({ platform: platform }).flatMap((book) => book.prefs);

    const chains = recipes.flatMap((recipe) => {
      if (recipe.src.isAbsolute) {
        return this.travarseSync(recipe);
      }
      if (platform == "default") {
        return this.travarseSync(recipe, { prefix: ResLayout.recipe().join(platform) });
      }
      return [
        ...this.travarseSync(recipe, { prefix: ResLayout.recipe().join(platform) }),
        ...this.travarseSync(recipe, { prefix: ResLayout.recipe().join("default") }),
      ];
    });

    const lines = chains
      .filter((chain) => this.allows(chain.src))
      .toSorted((a, b) => a.dst < b.dst ? -1 : 1)
      .map((chain) => this.format(chain));

    const encoder = new TextEncoder();
    const bytes = encoder.encode(lines.join("\n") + "\n");

    await streams.writeAll(this.context.stream, bytes);
  }

  private format(chain: PrefChain): string {
    const color = this.colored
      ? Result.run(() => chain.dst.lstatSync()).fold({
        onSuccess: (stat) => this.color(stat),
        onFailure: (_) => Color.RED,
      })
      : undefined;

    const dst = color ? color.apply(chain.dst.toString()) : chain.dst.toString();
    const src = chain.src.toString();

    switch (this.context.long) {
      case true:
        return [dst, src].join(" -> ");

      case false:
        return dst;
    }
  }

  private color(stat: Deno.FileInfo): Color {
    if (stat.isSymlink) {
      return Color.MAGENTA;
    }
    if (stat.isDirectory) {
      return Color.BLUE;
    }
    if (stat.isFile) {
      return Color.RESET;
    }
    return Color.RESET;
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
  logger?: Lumber;
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
      this.context.logger?.mark(sprintf("%s Launched (%02d/%02d)", book.name, i + 1, books.length), { bold: true });

      for (const recipe of book.prefs) {
        await this.linkPref(recipe);
      }
      for (const recipe of book.snips) {
        await this.enableSnip(recipe);
      }
      if (this.context.activate) {
        await this.activate(book);
      }
    }
  }

  private cleanup(books: CookBook[]): Promise<void> {
    const action = new CleanupAction(this.context);
    return action.perform(books);
  }

  private async linkPref(recipe: PrefRecipe): Promise<void> {
    const identity = await unix.identify();

    const chains = run(() => {
      if (recipe.src.isAbsolute) {
        return this.travarseSync(recipe);
      }
      if (identity == "default") {
        return this.travarseSync(recipe, { prefix: ResLayout.recipe().join(identity) });
      }
      return [
        ...this.travarseSync(recipe, { prefix: ResLayout.recipe().join(identity) }),
        ...this.travarseSync(recipe, { prefix: ResLayout.recipe().join("default") }),
      ];
    });

    for (const chain of chains) {
      if (!this.allows(chain.src)) {
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
      if (!dirStat || dirStat.isDirectory) {
        await shell.mkdirp(dir, this.shellOptions);
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

  private async enableSnip(recipe: SnipRecipe): Promise<void> {
    const chains = run(() => {
      if (recipe.src.isAbsolute) {
        return this.travarseSync(recipe);
      } else {
        return this.travarseSync(recipe, { prefix: ResLayout.snippet() });
      }
    });

    for (const chain of chains) {
      if (!this.allows(chain.src)) {
        this.context.logger?.debug(`File ignored: ${chain.src}`);
        continue;
      }
      const srcStat = await Result.runAsyncOr(() => chain.src.lstat());
      if (!srcStat) {
        this.context.logger?.info(`File not found: ${chain.src}`);
        continue;
      }

      const srcText = await Deno.readTextFile(chain.src.toString()).then((text) => text.trim());
      const dstText = await Result.runAsyncOr(() => Deno.readTextFile(chain.dst.toString()));

      if (dstText && dstText.includes(srcText)) {
        this.context.logger?.info(`Snippet already enabled in file: ${chain.dst}`);
        continue;
      }

      this.context.logger?.info(`Enable snippet: ${chain.src} >> ${chain.dst}`);

      if (this.context.dryRun) {
        continue;
      }

      const newText = run(() => {
        if (dstText && dstText.trim().length > 0) {
          return dstText.trim() + "\n" + srcText + "\n";
        } else {
          return srcText + "\n";
        }
      });

      const encoder = new TextEncoder();

      Deno.writeFile(chain.dst.toFileUrl(), encoder.encode(newText));
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
  logger?: Lumber;
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
      this.context.logger?.mark(sprintf("%s Launched (%02d/%02d)", book.name, i + 1, books.length), { bold: true });

      if (this.context.deactivate) {
        await this.deactivate(book);
      }
      for (const recipe of book.snips) {
        await this.disableSnip(recipe);
      }
      for (const recipe of book.prefs) {
        await this.unlinkPref(recipe);
      }
    }
  }

  private cleanup(books: CookBook[]): Promise<void> {
    const action = new CleanupAction(this.context);
    return action.perform(books);
  }

  private async unlinkPref(recipe: PrefRecipe): Promise<void> {
    const identity = await unix.identify();

    const chains = run(() => {
      if (recipe.src.isAbsolute) {
        return this.travarseSync(recipe);
      }
      if (identity == "default") {
        return this.travarseSync(recipe, { prefix: ResLayout.recipe().join(identity) });
      }
      return [
        ...this.travarseSync(recipe, { prefix: ResLayout.recipe().join(identity) }),
        ...this.travarseSync(recipe, { prefix: ResLayout.recipe().join("default") }),
      ];
    });

    for (const chain of chains) {
      if (!this.allows(chain.src)) {
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

  private async disableSnip(recipe: SnipRecipe): Promise<void> {
    const chains = run(() => {
      if (recipe.src.isAbsolute) {
        return this.travarseSync(recipe);
      } else {
        return this.travarseSync(recipe, { prefix: ResLayout.snippet() });
      }
    });

    for (const chain of chains) {
      if (!this.allows(chain.src)) {
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
        this.context.logger?.info(`File not found: ${chain.dst}`);
        continue;
      }
      const dstText = await Result.runAsyncOr(() => Deno.readTextFile(chain.dst.toString()));
      if (!dstText) {
        this.context.logger?.info(`Fiel is empty: ${chain.dst}`);
        continue;
      }

      const srcText = await Deno.readTextFile(chain.src.toString());
      if (dstText && !dstText.includes(srcText)) {
        this.context.logger?.info(`Snippet already disabled in file: ${chain.dst}`);
        continue;
      }

      this.context.logger?.info(`Disable snippet: ${chain.src} << ${chain.dst}`);

      if (this.context.dryRun) {
        continue;
      }

      const newText = dstText.replaceAll(srcText, "");
      const encoder = new TextEncoder();

      Deno.writeFile(chain.dst.toFileUrl(), encoder.encode(newText));
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
  logger?: Lumber;
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

    return this.perform(books);
  }

  async perform(books: CookBook[]): Promise<void> {
    const banner = "Scanning broken symlinks";
    this.context.logger?.info(`${banner}...\r`, { term: false });

    const recipes = books
      .flatMap((book) => book.prefs)
      .toSorted((a, b) => a.dst.expandHome() < b.dst.expandHome() ? -1 : 1);

    const found: Path[] = [];
    for (const recipe of recipes) {
      const path = recipe.dst.expandHome();

      if (recipe.options?.autoclean == false) {
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
      this.context.logger?.debug(`Found ${found.length} broken symlinks`);
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