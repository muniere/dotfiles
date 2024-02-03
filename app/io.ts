import * as io from "stdlib/io/mod.ts";

export interface Fiber {
  isTerminal(): boolean;
  writeAll(data: Uint8Array): Promise<void>;
  writeAllSync(data: Uint8Array): void;
}

export class ConsoleFiber implements Fiber {
  static readonly instance = new ConsoleFiber();

  private constructor() {}

  isTerminal(): boolean {
    return Deno.stdout.isTerminal();
  }

  writeAll(data: Uint8Array): Promise<void> {
    return io.writeAll(Deno.stdout, data);
  }

  writeAllSync(data: Uint8Array): void {
    io.writeAllSync(Deno.stdout, data);
  }
}

export class WriterFiber implements Fiber {
  isTerminal(): boolean {
    return this.writer === Deno.stdout && Deno.stdout.isTerminal();
  }

  private readonly writer: io.Writer & io.WriterSync;

  constructor(writer: io.Writer & io.WriterSync) {
    this.writer = writer;
  }

  writeAll(data: Uint8Array): Promise<void> {
    return io.writeAll(this.writer, data);
  }

  writeAllSync(data: Uint8Array): void {
    io.writeAllSync(this.writer, data);
  }
}
