import { Path } from "../lib/path.ts";

export class HomeLayout {
  private constructor() {}

  static bin(): Path {
    return new Path("~/.local/bin").expandHome();
  }

  static cache(): Path {
    return new Path("~/.cache").expandHome();
  }

  static config(): Path {
    return new Path("~/.config").expandHome();
  }

  static data(): Path {
    return new Path("~/.local/share").expandHome();
  }

  static state(): Path {
    return new Path("~/.local/state").expandHome();
  }

  static runtime(): Path {
    return new Path("~/.local/run").expandHome();
  }
}

export class ResLayout {
  private constructor() {}

  static pref(): Path {
    return new Path("./pref");
  }

  static snip(): Path {
    return new Path("./snip");
  }

  static tmpl(): Path {
    return new Path("./tmpl");
  }
}
