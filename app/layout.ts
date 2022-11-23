import { Path } from "./path.ts";

export class HomeLayout {
  private constructor() {}

  static bin(): Path {
    return HomeLayout.env("XDG_BIN_HOME", "~/.local/bin");
  }

  static cache(): Path {
    return HomeLayout.env("XDG_CACHE_HOME", "~/.cache");
  }

  static config(): Path {
    return HomeLayout.env("XDG_CONFIG_HOME", "~/.config");
  }

  static data(): Path {
    return HomeLayout.env("XDG_DATA_HOME", "~/.local/share");
  }

  static state(): Path {
    return HomeLayout.env("XDG_STATE_HOME", "~/.local/state");
  }

  static runtime(): Path {
    return HomeLayout.env("XDG_RUNTIME_HOME", "~/.local/run");
  }

  private static env(key: string, orElse: string): Path {
    return new Path(Deno.env.get(key) ?? orElse).expandHome();
  }
}

export class ResLayout {
  private constructor() {}

  static recipe(): Path {
    return new Path("./recipe");
  }

  static snippet(): Path {
    return new Path("./snippet");
  }
}
