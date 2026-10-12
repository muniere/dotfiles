package vifm

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var VifmCookBook = &chef.CookBook{
	Name:      "VifmCookBook",
	Container: layout.Vault().Join("vifm/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("vifm/"),
		}),
	},
}
