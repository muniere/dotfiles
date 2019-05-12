class Target:

    DOTFILE = "dotfile"
    BINFILE = "binfile"
    BREW = "brew"
    CASK = "cask"
    GEM = "gem"
    NPM = "npm"

    @classmethod
    def values(cls):
        return [
            cls.DOTFILE,
            cls.BINFILE,
            cls.BREW,
            cls.CASK,
            cls.GEM,
            cls.NPM,
        ]
