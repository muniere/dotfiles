package ghostty

import (
	"errors"
	"io/fs"
	"os"
	"strings"
	"text/template"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
	"github.com/muniere/dotfiles/internal/theme"
)

var GhosttyCookBook = &chef.CookBook{
	Name:      "GhosttyCookBook",
	Container: layout.Vault().Join("ghostty/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("ghostty/"),
		}),
	},
	Setup: func(options shell.Options) error {
		// template: render the theme of the vault with the color palette
		{
			src := layout.Vault().Join("ghostty", "template", "themes", "muniere")
			dst := layout.Vault().Join("ghostty", "default", "themes", "muniere")

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

			if !options.DryRun {
				if err := os.WriteFile(dst.String(), []byte(content), 0o666); err != nil {
					return err
				}
			}
		}

		// config
		{
			dir := layout.Home.Config().Join("ghostty", "conf.d")
			file := dir.Join("local.ghostrc")

			if !options.DryRun {
				if err := os.MkdirAll(dir.String(), 0o777); err != nil {
					return err
				}

				created, err := os.OpenFile(file.String(), os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o666)
				if errors.Is(err, fs.ErrExist) {
					return nil
				}
				if err != nil {
					return err
				}
				if err := created.Close(); err != nil {
					return err
				}
			}

			options.Logger.Debugf("Create a file %s with empty content", file)
		}
		return nil
	},
}
