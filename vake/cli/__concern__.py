from .. import concern
from .__target__ import Target

class Concern:

    @classmethod
    def hunt(cls, target):
        if target == Target.DOTFILE:
            return concern.dotfile

        if target == Target.BREW:
            return concern.brew

        if target == Target.CASK:
            return concern.cask

        if target == Target.GEM:
            return concern.gem

        if target == Target.NPM:
            return concern.npm

        if target == Target.BINFILE:
            return concern.binfile

        return None

    @classmethod
    def installable(cls, x):
        return x is not None and x.Install is not None

    @classmethod
    def uninstallable(cls, x):
        return x is not None and x.Uninstall is not None

    @classmethod
    def statusable(cls, x):
        return x is not None and x.Status is not None
