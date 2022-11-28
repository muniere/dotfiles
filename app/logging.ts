import * as streams from "https://deno.land/std@0.163.0/streams/mod.ts";
import * as colors from "https://deno.land/std@0.163.0/fmt/colors.ts";
import { Pipeline, run } from "./lang.ts";

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
    private readonly values: Map<LogLevel, Pipeline<string>>,
  ) {}

  static default(): LogPalette {
    return new LogPalette(
      new Map([
        [LogLevel.DEBUG, Pipeline.of(colors.green)],
        [LogLevel.TRACE, Pipeline.of(colors.magenta)],
        [LogLevel.MARK, Pipeline.of(colors.white)],
        [LogLevel.INFO, Pipeline.of(colors.cyan)],
        [LogLevel.WARN, Pipeline.of(colors.yellow)],
        [LogLevel.ERROR, Pipeline.of(colors.red)],
      ]),
    );
  }

  get(level: LogLevel): Pipeline<string> {
    return this.values.get(level) ?? Pipeline.of(colors.reset);
  }
}

export type LogOptions = {
  bold?: boolean;
  term?: boolean;
  async?: boolean;
};

export class Logger {
  level: LogLevel;

  private readonly stream: LogStream;
  private readonly palette: LogPalette;

  private static readonly encoder: TextEncoder = new TextEncoder();
  private static readonly terminator = "\n";

  constructor(nargs: {
    level: LogLevel;
    stream?: LogStream;
    palette?: LogPalette;
  }) {
    this.level = nargs.level ?? LogLevel.DEBUG;
    this.stream = nargs.stream ?? Deno.stdout;
    this.palette = nargs.palette ?? LogPalette.default();
  }

  log(message: string, level: LogLevel, options: LogOptions = {}): void {
    if (level.value < this.level.value) {
      return;
    }

    const decorate = run(() => {
      if (options.bold) {
        return this.palette.get(level).concat(colors.bold);
      } else {
        return this.palette.get(level);
      }
    });

    const terminator = options.term == false ? "" : Logger.terminator;
    const plainMessage = `[${level.label.padEnd(5)}] ${message}${terminator}`;
    const coloredMessage = decorate.perform(plainMessage);
    const bytes = Logger.encoder.encode(coloredMessage);

    if (options.async == true) {
      streams.writeAll(this.stream, bytes);
    } else {
      streams.writeAllSync(this.stream, bytes);
    }
  }

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
