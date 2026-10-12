package launchd

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var LaunchdCookBook = &chef.CookBook{
	Name:      "LaunchdCookBook",
	Container: layout.Vault().Join("launchd/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Data().Join("zsh/site-functions/"),
		}),
	},
}
