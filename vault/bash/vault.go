package bash

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var BashCookBook = &chef.CookBook{
	Name:      "BashCookBook",
	Container: layout.Vault().Join("bash/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("bash/"),
		}),
	},
	Tmpls: []*chef.TmplSpec{
		chef.Tmpl(chef.Bind{
			Src: "bash_profile",
			Dst: "~/.bash_profile",
		}, chef.TmplOptions{Values: map[string]any{
			"cache":   layout.Home.Cache().TransHome(),
			"config":  layout.Home.Config().TransHome(),
			"data":    layout.Home.Data().TransHome(),
			"state":   layout.Home.State().TransHome(),
			"runtime": layout.Home.Runtime().TransHome(),
		}}),
		chef.Tmpl(chef.Bind{
			Src: "bashrc",
			Dst: "~/.bashrc",
		}, chef.TmplOptions{Values: map[string]any{
			"cache":   layout.Home.Cache().TransHome(),
			"config":  layout.Home.Config().TransHome(),
			"data":    layout.Home.Data().TransHome(),
			"state":   layout.Home.State().TransHome(),
			"runtime": layout.Home.Runtime().TransHome(),
		}}),
	},
}
