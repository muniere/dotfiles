package xcode

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/platform"
)

var XcodeCookBook = &chef.CookBook{
	Name:      "XcodeCookBook",
	Container: layout.Vault().Join("Xcode/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: "./UserData/FontAndColorThemes",
			Dst: "~/Library/Developer/Xcode/UserData/FontAndColorThemes",
		}),
		chef.Pref(chef.Bind{
			Src: "./UserData/KeyBindings",
			Dst: "~/Library/Developer/Xcode/UserData/KeyBindings",
		}),
	},
	Platforms: []platform.Platform{platform.Darwin},
}
