import * as fs from "https://deno.land/std@0.163.0/fs/mod.ts";

import { Path, PathLike } from "./path.ts";
import { Platform } from "./unix.ts";

import * as shell from "./shell.ts";

// =====
// Shared
// =====
export type PathBind = {
  src: PathLike;
  dst: PathLike;
};

export abstract class ChainBase {
  readonly src: Path;
  readonly dst: Path;

  constructor(bind: PathBind) {
    this.src = new Path(bind.src);
    this.dst = new Path(bind.dst);
  }
}

export abstract class RecipeBase<Chain extends ChainBase> {
  readonly src: Path;
  readonly dst: Path;

  constructor(bind: PathBind) {
    this.src = new Path(bind.src);
    this.dst = new Path(bind.dst);
  }

  abstract chain(bind: PathBind): Chain;
}

// =====
// Preferences
// =====
export type PrefLinkKind = "link" | "copy";

export type PrefLinkOptions = {
  kind?: PrefLinkKind;
};

export type PrefChainOptions = PrefLinkOptions;

export class PrefChain extends ChainBase {
  readonly options?: PrefChainOptions;

  constructor(bind: PathBind, options?: PrefChainOptions) {
    super(bind);
    this.options = options;
  }
}

export type PrefRecipeOptions = PrefLinkOptions & {
  autoclean?: boolean;
};

export class PrefRecipe extends RecipeBase<PrefChain> {
  readonly options?: PrefRecipeOptions;

  constructor(bind: PathBind, options?: PrefRecipeOptions) {
    super(bind);
    this.options = options;
  }

  static glob(bind: PathBind, options?: PrefRecipeOptions): PrefRecipe[] {
    const pattern = new Path(bind.dst).expandHome().toString();

    return [...fs.expandGlobSync(pattern)].map((entry) =>
      new PrefRecipe({
        src: new Path(bind.src),
        dst: new Path(entry.path).expandHome(),
      }, options)
    );
  }

  override chain(bind: PathBind): PrefChain {
    return new PrefChain(bind, this.options);
  }
}

// =====
// Snippets
// =====
export class SnipChain extends ChainBase {
  constructor(bind: PathBind) {
    super(bind);
  }
}

export class SnipRecipe extends RecipeBase<SnipChain> {
  override chain(bind: PathBind): SnipChain {
    return new SnipChain(bind);
  }
}

// =====
// CookBook
// =====
export type CookBookCallback = (options: shell.CallOptions) => Promise<void>;

export class CookBook {
  private _name: string;
  private _prefs: PrefRecipe[];
  private _snips: SnipRecipe[];
  private _platforms: Platform[] | undefined;
  private _activate: CookBookCallback | undefined;
  private _deactivate: CookBookCallback | undefined;

  constructor(nargs: {
    name: string;
    prefs?: PrefRecipe[];
    snips?: SnipRecipe[];
    platforms?: Platform[];
    activate?: CookBookCallback;
    deactivate?: CookBookCallback;
  }) {
    this._name = nargs.name;
    this._prefs = [...(nargs.prefs ?? [])];
    this._snips = [...(nargs.snips ?? [])];
    this._platforms = nargs.platforms;
    this._activate = nargs.activate;
    this._deactivate = nargs.deactivate;
  }

  get name(): string {
    return this._name;
  }

  get prefs(): PrefRecipe[] {
    return this._prefs;
  }

  get snips(): SnipRecipe[] {
    return this._snips;
  }

  supports(platform: Platform): boolean {
    return !this._platforms || this._platforms.includes(platform);
  }

  async activate(options: shell.CallOptions): Promise<void> {
    const fn = this._activate;
    if (fn) {
      await fn(options);
    }
  }

  async deactivate(options: shell.CallOptions): Promise<void> {
    const fn = this._deactivate;
    if (fn) {
      await fn(options);
    }
  }
}
