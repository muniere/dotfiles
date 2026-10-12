package bat

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var BatCookBook = &chef.CookBook{
	Name:      "BatCookBook",
	Container: layout.Vault().Join("bat/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("bat/"),
		}),
	},
}
