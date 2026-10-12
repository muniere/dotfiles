package asdf

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var AsdfCookBook = &chef.CookBook{
	Name:      "AsdfCookBook",
	Container: layout.Vault().Join("asdf/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("asdf/"),
		}),
	},
}
