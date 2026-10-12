package zshprompt

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
)

var ZshPromptCookBook = &chef.CookBook{
	Name:      "ZshPromptCookBook",
	Container: layout.Vault().Join("zsh-prompt/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: "bin/",
			Dst: layout.Home.Bin(),
		}),
		chef.Pref(chef.Bind{
			Src: "zprompt.zsh",
			Dst: layout.Home.Data().Join("zsh/prompt/zprompt.zsh"),
		}),
		chef.Pref(chef.Bind{
			Src: "themes/",
			Dst: layout.Home.Data().Join("zsh/prompt/themes/"),
		}),
		chef.Pref(chef.Bind{
			Src: "completion/",
			Dst: layout.Home.Data().Join("zsh/site-functions/"),
		}),
	},
}
