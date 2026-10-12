package desktop

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/platform"
	"github.com/muniere/dotfiles/internal/shell"
)

var HomeCookBook = &chef.CookBook{
	Name:      "HomeCookBook",
	Container: layout.Vault().Join("desktop/"),
	Activate: func(options shell.Options) error {
		dirs := []struct {
			path fspath.Path
			mode uint32
		}{
			{path: layout.Home.Bin(), mode: 0o755},
			{path: layout.Home.Cache(), mode: 0o755},
			{path: layout.Home.Config(), mode: 0o755},
			{path: layout.Home.Data(), mode: 0o755},
			{path: layout.Home.State(), mode: 0o755},
			{path: layout.Home.Runtime(), mode: 0o700},
		}

		for _, dir := range dirs {
			if stat, err := dir.path.Stat(); err == nil {
				if stat.IsDir() {
					options.Logger.Infof("Directory already exists: %s", dir.path)
				} else {
					options.Logger.Warnf("File already exists, not a directory: %s", dir.path)
				}
				continue
			}

			if _, err := shell.Mkdir(dir.path, shell.MkdirOptions{Options: options, Mode: dir.mode}); err != nil {
				return err
			}
		}
		return nil
	},
}

// LibraryCookBook gives "Application Support" a name without a space.
var LibraryCookBook = &chef.CookBook{
	Name:      "LibraryCookBook",
	Container: layout.Vault().Join("desktop/"),
	Activate: func(options shell.Options) error {
		src := fspath.Path("~/Library/Application Support").ExpandHome()
		dst := fspath.Path("~/Library/ApplicationSupport").ExpandHome()

		if stat, err := dst.Stat(); err == nil {
			if stat.IsDir() {
				options.Logger.Infof("Directory already exists: %s", dst)
			} else {
				options.Logger.Warnf("File already exists, not a directory: %s", dst)
			}
			return nil
		}

		_, err := shell.Symlink(src, dst, options)
		return err
	},
	Platforms: []platform.Platform{platform.Darwin},
}
