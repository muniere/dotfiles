package mise

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/platform"
)

var MiseCookBook = &chef.CookBook{
	Name:      "MiseCookBook",
	Container: layout.Vault().Join("mise/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("mise/"),
		}),
	},
}

var MiseCompletionCookBook = &chef.CookBook{
	Name:      "MiseCompletionCookBook",
	Container: layout.Vault().Join("mise/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: "/opt/homebrew/etc/bash_completion.d/mise",
			Dst: layout.Home.Data().Join("bash/bash_completion.d/mise"),
		}),
		chef.Pref(chef.Bind{
			Src: "/opt/homebrew/share/zsh/site-functions/_mise",
			Dst: layout.Home.Data().Join("zsh/site-functions/_mise"),
		}),
	},
	Platforms: []platform.Platform{platform.Darwin},
}
