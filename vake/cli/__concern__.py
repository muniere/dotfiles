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
