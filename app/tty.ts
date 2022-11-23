export class Color {
  static readonly BLACK = new Color(30);
  static readonly RED = new Color(31);
  static readonly GREEN = new Color(32);
  static readonly YELLOW = new Color(33);
  static readonly BLUE = new Color(34);
  static readonly MAGENTA = new Color(35);
  static readonly CYAN = new Color(36);
  static readonly WHITE = new Color(37);
  static readonly RESET = new Color(39);

  readonly code: number;

  private constructor(code: number) {
    this.code = code;
  }

  apply(
    message: string,
    options: { bold?: boolean } = {},
  ): string {
    const base = `${this}${message}${Color.RESET}`;
    return options.bold ? `\x1b[1m${base}\x1b[0m` : base;
  }

  toString(): string {
    return `\x1b[${this.code}m`;
  }
}
