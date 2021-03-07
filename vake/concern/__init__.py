from .__binfile import (
    InstallAction as BinfileInstallAction,
    UninstallAction as BinfileUninstallAction,
    StatusAction as BinfileStatusAction,
)

from .__dotfile import (
    InstallAction as DotfileInstallAction,
    UninstallAction as DotfileUninstallAction,
    StatusAction as DotfileStatusAction,
)

from .__brew import (
    InstallAction as BrewInstallAction,
    UninstallAction as BrewUninstallAction,
    StatusAction as BrewStatusAction,
)

from .__cask import (
    InstallAction as CaskInstallAction,
    UninstallAction as CaskUninstallAction,
    StatusAction as CaskStatusAction,
)
