package gradle

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var GradleCookBook = &chef.CookBook{
	Name:      "GradleCookBook",
	Container: layout.Vault().Join("gradle/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: "gradle.properties",
			Dst: layout.Home.Data().Join("gradle/gradle.properties"),
		}, chef.PrefOptions{
			Kind:        chef.PrefCopy,
			NoAutoclean: true,
		}),
	},
}
