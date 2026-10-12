package node

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
)

var NodeCookBook = &chef.CookBook{
	Name:      "NodeCookBook",
	Container: layout.Vault().Join("node/"),
	Activate: func(options shell.Options) error {
		dir := layout.Home.Data().Join("node")
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
