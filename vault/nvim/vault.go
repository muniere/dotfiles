package nvim

import (
	"os"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
	"github.com/muniere/dotfiles/vault/vi"
)

const plugURL = "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"

var NeovimCookBook = &chef.CookBook{
	Name:      "NeovimCookBook",
	Container: layout.Vault().Join("nvim/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: ".",
			Dst: layout.Home.Config().Join("nvim/"),
		}),
	},
	// Setup generates the color scheme into the vault.
	Setup: func(options shell.Options) error {
		scheme := vi.Muniere

		content := scheme.Render()
		dst := layout.Vault().Join("nvim", "default", "colors", fspath.Path(scheme.Name+".vim"))

		options.Logger.Debugf("Create a file %s with content:\n%s", dst, content)

		if options.DryRun {
			return nil
		}

		return os.WriteFile(dst.String(), []byte(content+"\n"), 0o666)
	},
	Activate: func(options shell.Options) error {
		file := layout.Home.Data().Join("nvim/site/autoload/plug.vim")

		if _, err := file.Stat(); err == nil {
			options.Logger.Infof("File already exists: %s", file)
			return nil
		}

		_, err := shell.Curl(plugURL, shell.CurlOptions{Options: options, Output: file})
		return err
	},
}
