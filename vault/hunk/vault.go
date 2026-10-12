package hunk

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

// hunk: review-first terminal diff viewer for agent-authored changesets.
// Reference: https://hunk.dev/
var HunkCookBook = &chef.CookBook{
	Name:      "HunkCookBook",
	Container: layout.Vault().Join("hunk/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("hunk/"),
		}),
	},
}
