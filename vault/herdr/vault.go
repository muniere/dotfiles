package herdr

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

// herdr: terminal workspace manager for AI coding agents.
// Reference: https://herdr.dev/docs/configuration/
var HerdrCookBook = &chef.CookBook{
	Name:      "HerdrCookBook",
	Container: layout.Vault().Join("herdr/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: "conf.d/",
			Dst: layout.Home.Config().Join("herdr/"),
		}),
		chef.Pref(chef.Bind{
			Src: "bin/",
			Dst: layout.Home.Bin(),
		}),
		chef.Pref(chef.Bind{
			Src: "completion/",
			Dst: layout.Home.Data().Join("zsh/site-functions/"),
		}),
	},
}
