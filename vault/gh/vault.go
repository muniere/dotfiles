package gh

import (
	"strings"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
)

var GitHubCookBook = &chef.CookBook{
	Name:      "GitHubCookBook",
	Container: layout.Vault().Join("gh/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Data().Join("gh/"),
		}),
	},
	Activate: func(options shell.Options) error {
		repos := []string{
			"muniere/gh-team",
		}

		which, err := shell.Capture("which", []string{"gh"}, shell.CaptureOptions{})
		if err != nil {
			return err
		}
		cmd := strings.TrimSpace(which.Stdout)
		if which.Status.Code != 0 || cmd == "" {
			options.Logger.Warnf("gh not found on PATH yet. skip.")
			return nil
		}

		for _, repo := range repos {
			if _, err := shell.Call(cmd, []string{"extension", "install", repo}, options); err != nil {
				return err
			}
		}
		return nil
	},
}
