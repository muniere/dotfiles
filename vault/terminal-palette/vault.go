package terminalpalette

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
)

var TerminalPaletteCookBook = &chef.CookBook{
	Name:      "TerminalPaletteCookBook",
	Container: layout.Vault().Join("terminal-palette/"),
	Setup: func(options shell.Options) error {
		url := "https://raw.githubusercontent.com/mgedmin/scripts/refs/heads/master/show-all-256-colors"
		path := layout.Home.Bin().Join("terminal-palette")

		if _, err := path.Stat(); err == nil {
			options.Logger.Infof("File already exists: %s", path)
			return nil
		}

		if _, err := shell.Curl(url, shell.CurlOptions{Options: options, Output: path}); err != nil {
			return err
		}

		_, err := shell.Chmod(path, "+x", options)
		return err
	},
}
