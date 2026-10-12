package rio

import (
	"os"
	"strings"
	"text/template"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
	"github.com/muniere/dotfiles/internal/theme"
)

var RioCookBook = &chef.CookBook{
	Name:      "RioCookBook",
	Container: layout.Vault().Join("rio/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("rio/"),
		}),
	},
	// Setup renders the theme of the vault with the color palette.
	Setup: func(options shell.Options) error {
		src := layout.Vault().Join("rio", "template", "themes", "muniere.toml")
		dst := layout.Vault().Join("rio", "default", "themes", "muniere.toml")

		source, err := os.ReadFile(src.String())
		if err != nil {
			return err
		}

		tmpl, err := template.New(src.String()).Parse(string(source))
		if err != nil {
			return err
		}

		var rendered strings.Builder
		if err := tmpl.Execute(&rendered, theme.Palette[:]); err != nil {
			return err
		}
		content := rendered.String()

		options.Logger.Debugf("Create a file %s with content:\n%s", dst, content)

		if options.DryRun {
			return nil
		}

		return os.WriteFile(dst.String(), []byte(content), 0o666)
	},
}
