package tmux

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var TmuxCookBook = &chef.CookBook{
	Name:      "TmuxCookBook",
	Container: layout.Vault().Join("tmux/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("tmux/"),
		}),
	},
}
