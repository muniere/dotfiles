import { Path } from "@dotfiles/lib/path.ts";

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

  static vault(): Path {
    return new Path("./vault");
  }
}
