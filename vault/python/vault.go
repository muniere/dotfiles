package python

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var PythonCookBook = &chef.CookBook{
	Name:      "PythonCookBook",
	Container: layout.Vault().Join("python/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("python/"),
		}),
	},
}
