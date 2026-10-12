package sqlfluff

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var SqlfluffCookBook = &chef.CookBook{
	Name:      "SqlfluffCookBook",
	Container: layout.Vault().Join("sqlfluff/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("sqlfluff/"),
		}),
	},
}
