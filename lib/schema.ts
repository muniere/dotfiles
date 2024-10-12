import * as fs from "@std/fs";

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

export abstract class SpecBase<Chain extends ChainBase> {
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

export type PrefSpecOptions = PrefLinkOptions & {
  autoclean?: boolean;
};

export class PrefSpec extends SpecBase<PrefChain> {
  readonly options?: PrefSpecOptions;

  constructor(bind: PathBind, options?: PrefSpecOptions) {
    super(bind);
    this.options = options;
  }

  static glob(bind: PathBind, options?: PrefSpecOptions): PrefSpec[] {
    const pattern = new Path(bind.dst).expandHome().toString();

    return [...fs.expandGlobSync(pattern)].map((entry) =>
      new PrefSpec({
        src: new Path(bind.src),
        dst: new Path(entry.path).expandHome(),
      }, options)
    );
  }

  static globp(bind: PathBind & { children: string[] }, options?: PrefSpecOptions): PrefSpec[] {
    const pattern = new Path(bind.dst).expandHome().toString();

    return [...fs.expandGlobSync(pattern)].flatMap(
      (entry) =>
        bind.children.map((path) =>
          new PrefSpec({
            src: new Path(bind.src, path),
            dst: new Path(entry.path, path).expandHome(),
          }, options)
        ),
    );
  }
  override chain(bind: PathBind): PrefChain {
    return new PrefChain(bind, this.options);
  }
}

// =====
// Templates
// =====
export type TmplOptions = {
  values?: object;
};

export type TmplChainOptions = TmplOptions;

export class TmplChain extends ChainBase {
  readonly options?: TmplChainOptions;

  constructor(bind: PathBind, options?: TmplChainOptions) {
    super(bind);
    this.options = options;
  }
}

export type TmplSpecOptions = TmplOptions;

export class TmplSpec extends SpecBase<TmplChain> {
  readonly options?: TmplSpecOptions;

  constructor(bind: PathBind, options?: TmplSpecOptions) {
    super(bind);
    this.options = options;
  }

  override chain(bind: PathBind): TmplChain {
    return new TmplChain(bind, this.options);
  }
}

// =====
// CookBook
// =====
export type CookBookCallback = (options: shell.CallOptions) => Promise<void>;

export class CookBook {
  private _name: string;
  private _container: Path;
  private _prefs: PrefSpec[];
  private _tmpls: TmplSpec[];
  private _platforms: Platform[] | undefined;
  private _activate: CookBookCallback | undefined;
  private _deactivate: CookBookCallback | undefined;

  constructor(nargs: {
    name: string;
    container: Path;
    prefs?: PrefSpec[];
    tmpls?: TmplSpec[];
    platforms?: Platform[];
    activate?: CookBookCallback;
    deactivate?: CookBookCallback;
  }) {
    this._name = nargs.name;
    this._prefs = [...(nargs.prefs ?? [])];
    this._tmpls = [...(nargs.tmpls ?? [])];
    this._container = nargs.container;
    this._platforms = nargs.platforms;
    this._activate = nargs.activate;
    this._deactivate = nargs.deactivate;
  }

  get name(): string {
    return this._name;
  }

  get prefs(): PrefSpec[] {
    return this._prefs;
  }

  get tmpls(): TmplSpec[] {
    return this._tmpls;
  }

  get container(): Path {
    return this._container;
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
