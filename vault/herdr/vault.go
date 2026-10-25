package herdr

import (
	"strings"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
)

// herdr: terminal workspace manager for AI coding agents.
// Reference: https://herdr.dev/docs/configuration/
var HerdrCookBook = &chef.CookBook{
	Name:      "HerdrCookBook",
	Container: layout.Vault().Join("herdr/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: "conf.d/",
			Dst: layout.Home.Config().Join("herdr/"),
		}),
		chef.Pref(chef.Bind{
			Src: "bin/",
			Dst: layout.Home.Bin(),
		}),
		chef.Pref(chef.Bind{
			Src: "completion/",
			Dst: layout.Home.Data().Join("zsh/site-functions/"),
		}),
	},
	// Activate links the local plugins in place, so edits to them take effect
	// without relinking. Linking is idempotent and needs no running server.
	// Reference: https://herdr.dev/docs/plugins/
	Activate: func(options shell.Options) error {
		plugins := []string{
			"workspace-meta",
		}

		which, err := shell.Capture("which", []string{"herdr"}, shell.CaptureOptions{})
		if err != nil {
			return err
		}
		cmd := strings.TrimSpace(which.Stdout)
		if which.Status.Code != 0 || cmd == "" {
			options.Logger.Warnf("herdr not found on PATH yet. skip.")
			return nil
		}

		for _, plugin := range plugins {
			dir := layout.Vault().Join("herdr/default/plugins", fspath.Path(plugin)).ToAbsolute()
			if _, err := shell.Call(cmd, []string{"plugin", "link", dir.String()}, options); err != nil {
				return err
			}
		}
		return nil
	},
}
