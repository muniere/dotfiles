// Package layout tells where things live, in the home directory and in the repository.
package layout

import "github.com/muniere/dotfiles/internal/fspath"

type home struct{}

var Home home

func (home) Bin() fspath.Path {
	return fspath.Path("~/.local/bin").ExpandHome()
}

func (home) Cache() fspath.Path {
	return fspath.Path("~/.cache").ExpandHome()
}

func (home) Config() fspath.Path {
	return fspath.Path("~/.config").ExpandHome()
}

func (home) Data() fspath.Path {
	return fspath.Path("~/.local/share").ExpandHome()
}

func (home) State() fspath.Path {
	return fspath.Path("~/.local/state").ExpandHome()
}

func (home) Runtime() fspath.Path {
	return fspath.Path("~/.local/run").ExpandHome()
}

// Vault is the directory of the files to link, relative to the repository root.
func Vault() fspath.Path {
	return fspath.New("./vault")
}
