import * as path from "stdlib/path/mod.ts";
import * as fs from "stdlib/fs/mod.ts";

export type PathLike = Path | string;

export class Path {
  private readonly value: string;

  constructor(...values: PathLike[]) {
    this.value = path.join(...values.map((x) => x.toString()));
  }

  get isAbsolute(): boolean {
    return path.isAbsolute(this.value);
  }

  toAbsolute(): Path {
    const newValue = this.isAbsolute ? this.value : path.resolve(this.value);
    return new Path(newValue);
  }

  stat(): Promise<Deno.FileInfo> {
    return Deno.stat(this.value);
  }

  statSync(): Deno.FileInfo {
    return Deno.statSync(this.value);
  }

  lstat(): Promise<Deno.FileInfo> {
    return Deno.lstat(this.value);
  }

  lstatSync(): Deno.FileInfo {
    return Deno.lstatSync(this.value);
  }

  readDir(): AsyncIterable<Deno.DirEntry> {
    return Deno.readDir(this.value);
  }

  async *walk(options: fs.WalkOptions = {}): AsyncIterableIterator<fs.WalkEntry> {
    for await (const entry of fs.walk(this.value, options)) {
      yield entry;
    }
  }

  *walkSync(options: fs.WalkOptions = {}): IterableIterator<fs.WalkEntry> {
    for (const entry of fs.walkSync(this.value, options)) {
      yield entry;
    }
  }

  normalize(): Path {
    return new Path(path.normalize(this.value));
  }

  basename(): Path {
    return new Path(path.basename(this.value));
  }

  dirname(): Path {
    return new Path(path.dirname(this.value));
  }

  relative(other: PathLike): Path {
    return new Path(
      path.relative(
        /* from = */ other.toString(),
        /* to = */ this.value,
      ),
    );
  }

  join(...others: PathLike[]): Path {
    return new Path(
      path.join(this.value, ...others.map((x) => x.toString())),
    );
  }

  expandHome(): Path {
    const home = Deno.env.get("HOME");
    if (!home) {
      return this;
    }
    return new Path(this.value.replace(/^~/, home));
  }

  reduceHome(): Path {
    const home = Deno.env.get("HOME");
    if (!home) {
      return this;
    }
    return new Path(this.value.replace(home, "~"));
  }

  transHome(): Path {
    const home = Deno.env.get("HOME");
    if (!home) {
      return this;
    }
    return new Path(this.value.replace(home, "$HOME"));
  }

  match(regexp: string | RegExp): RegExpMatchArray | null {
    return this.value.match(regexp);
  }

  toFileUrl(): URL {
    return path.toFileUrl(this.toAbsolute().toString());
  }

  toString(): string {
    return this.value;
  }
}

export class PathFilter {
  private readonly whitelist: RegExp[];
  private readonly blacklist: RegExp[];

  constructor(nargs: {
    whitelist?: RegExp[];
    blacklist?: RegExp[];
  }) {
    this.whitelist = [...(nargs.whitelist ?? [])];
    this.blacklist = [...(nargs.blacklist ?? [])];
  }

  static glob(nargs: {
    whitelist?: string[];
    blacklist?: string[];
  }): PathFilter {
    return new PathFilter({
      whitelist: nargs.whitelist?.map((glob) => path.globToRegExp(glob)),
      blacklist: nargs.blacklist?.map((glob) => path.globToRegExp(glob)),
    });
  }

  static whitelist(globs: string[]): PathFilter {
    return this.glob({ whitelist: globs });
  }

  static blacklist(globs: string[]): PathFilter {
    return this.glob({ blacklist: globs });
  }

  test(path: PathLike): boolean {
    if (this.whitelist.some((regexp) => path.match(regexp))) {
      return true;
    }
    if (this.blacklist.some((regexp) => path.match(regexp))) {
      return false;
    }
    return true;
  }
}
