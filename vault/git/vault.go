package git

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
)

var GitCookBook = &chef.CookBook{
	Name:      "GitCookBook",
	Container: layout.Vault().Join("git/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: "config",
			Dst: layout.Home.Config().Join("git/config"),
		}),
		chef.Pref(chef.Bind{
			Src: "conf.d",
			Dst: layout.Home.Config().Join("git/conf.d/"),
		}),
		chef.Pref(chef.Bind{
			Src: "bin",
			Dst: layout.Home.Bin(),
		}),
	},
	Activate: func(options shell.Options) error {
		dir := layout.Home.Config().Join("git/conf.d/")
		file := dir.Join("config.extension")

		if _, err := dir.Stat(); err != nil {
			if _, err := shell.Mkdir(dir, shell.MkdirOptions{Options: options}); err != nil {
				return err
			}
		}

		if _, err := file.Stat(); err == nil {
			options.Logger.Infof("File already exists: %s", file)
			return nil
		}

		_, err := shell.Touch(file, options)
		return err
	},
}
