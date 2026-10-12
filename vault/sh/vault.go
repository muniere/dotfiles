package sh

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var ShCookBook = &chef.CookBook{
	Name:      "ShCookBook",
	Container: layout.Vault().Join("sh/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("sh/"),
		}),
	},
}
