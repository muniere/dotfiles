package tig

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
)

var TigCookBook = &chef.CookBook{
	Name:      "TigCookBook",
	Container: layout.Vault().Join("tig/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("tig/"),
		}),
	},
	Activate: func(options shell.Options) error {
		dir := layout.Home.Data().Join("tig")
		file := dir.Join("history")

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
