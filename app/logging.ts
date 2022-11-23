import * as streams from "https://deno.land/std@0.163.0/streams/mod.ts";

import { Color } from "./tty.ts";

export type LogStream =
  & Deno.Writer
  & Deno.WriterSync
  & Deno.Closer
  & { readonly rid: number };

export class LogLevel {
  static readonly DEBUG = new LogLevel({ value: 10, label: "DEBUG" });
  static readonly TRACE = new LogLevel({ value: 15, label: "TRACE" });
  static readonly MARK = new LogLevel({ value: 18, label: "MARK" });
  static readonly INFO = new LogLevel({ value: 20, label: "INFO" });
  static readonly WARN = new LogLevel({ value: 30, label: "WARN" });
  static readonly ERROR = new LogLevel({ value: 40, label: "ERROR" });

  readonly value: number;
  readonly label: string;

  private constructor(nargs: {
    value: number;
    label: string;
  }) {
    this.value = nargs.value;
    this.label = nargs.label;
  }
}

export class LogPalette {
  constructor(
    private readonly values: Map<LogLevel, Color>,
  ) {}

  static default(): LogPalette {
    return new LogPalette(
      new Map([
        [LogLevel.DEBUG, Color.GREEN],
        [LogLevel.TRACE, Color.MAGENTA],
        [LogLevel.MARK, Color.WHITE],
        [LogLevel.INFO, Color.CYAN],
        [LogLevel.WARN, Color.YELLOW],
        [LogLevel.ERROR, Color.RED],
      ]),
    );
  }

  get(level: LogLevel): Color {
    return this.values.get(level) ?? Color.RESET;
  }
}

export type LogOptions = {
  bold?: boolean;
  term?: boolean;
  async?: boolean;
};

export abstract class Lumber {
  abstract log(message: string, level: LogLevel, options: LogOptions): void;

  debug(message: string, options: LogOptions = {}): void {
    this.log(message, LogLevel.DEBUG, options);
  }
  trace(message: string, options: LogOptions = {}): void {
    this.log(message, LogLevel.TRACE, options);
  }
  mark(message: string, options: LogOptions = {}): void {
    this.log(message, LogLevel.MARK, options);
  }
  info(message: string, options: LogOptions = {}): void {
    this.log(message, LogLevel.INFO, options);
  }
  warn(message: string, options: LogOptions = {}): void {
    this.log(message, LogLevel.WARN, options);
  }
  error(message: string, options: LogOptions = {}): void {
    this.log(message, LogLevel.ERROR, options);
  }
}

export class StreamLumber extends Lumber {
  level: LogLevel = LogLevel.DEBUG;

  private readonly stream: LogStream;
  private readonly palette: LogPalette;

  private static readonly encoder: TextEncoder = new TextEncoder();
  private static readonly terminator = "\n";

  constructor(nargs: {
    stream?: LogStream;
    palette?: LogPalette;
  } = {}) {
    super();
    this.stream = nargs.stream ?? Deno.stdout;
    this.palette = nargs.palette ?? LogPalette.default();
  }

  log(message: string, level: LogLevel, options: LogOptions = {}): void {
    if (level.value < this.level.value) {
      return;
    }

    const terminator = options.term == false ? "" : StreamLumber.terminator;
    const plainMessage = `[${level.label.padEnd(5)}] ${message}${terminator}`;
    const coloredMessage = this.palette.get(level).apply(plainMessage, options);
    const bytes = StreamLumber.encoder.encode(coloredMessage);

    if (options.async == true) {
      streams.writeAll(this.stream, bytes);
    } else {
      streams.writeAllSync(this.stream, bytes);
    }
  }
}

export class NoopLumber extends Lumber {
  log(_message: string, _level: LogLevel, _options: LogOptions = {}): void {
    // do nothign
  }
}
