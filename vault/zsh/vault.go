package zsh

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var ZshCookBook = &chef.CookBook{
	Name:      "ZshCookBook",
	Container: layout.Vault().Join("zsh/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("zsh/"),
		}),
	},
	Tmpls: []*chef.TmplSpec{
		chef.Tmpl(chef.Bind{
			Src: "zshenv",
			Dst: "~/.zshenv",
		}, chef.TmplOptions{Values: map[string]any{
			"cache":   layout.Home.Cache().TransHome(),
			"config":  layout.Home.Config().TransHome(),
			"data":    layout.Home.Data().TransHome(),
			"state":   layout.Home.State().TransHome(),
			"runtime": layout.Home.Runtime().TransHome(),
		}}),
	},
}
