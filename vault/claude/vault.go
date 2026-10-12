package claude

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/layout"
)

var ClaudeCookBook = &chef.CookBook{
	Name:      "ClaudeCookBook",
	Container: layout.Vault().Join("claude/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: "bin/",
			Dst: fspath.Path("~/.claude/bin").ExpandHome(),
		}),
		chef.Pref(chef.Bind{
			Src: "hooks/",
			Dst: fspath.Path("~/.claude/hooks").ExpandHome(),
		}),
	},
}
