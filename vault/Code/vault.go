package code

import (
	"encoding/json"
	"os"
	"strings"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/shell"
)

var CodeCookBook = &chef.CookBook{
	Name:      "CodeCookBook",
	Container: layout.Vault().Join("Code/"),
	Activate: func(options shell.Options) error {
		container := layout.Vault().Join("Code/default/muniere-vscode-theme")
		manifest, err := readExtension(container)
		if err != nil {
			return err
		}

		installed, err := findExtension(manifest.Publisher, manifest.Name)
		if err != nil {
			return err
		}

		if installed != nil && installed.Version == manifest.Version {
			options.Logger.Infof(
				"Extension already installed: %s.%s@%s",
				installed.Publisher, installed.Name, installed.Version,
			)
			return nil
		}

		if installed != nil {
			options.Logger.Infof(
				"Extension already installed, but it's outdated: %s.%s@%s",
				installed.Publisher, installed.Name, installed.Version,
			)
		}

		options.Cwd = container.String()
		_, err = shell.Call("make", []string{"install"}, options)
		return err
	},
}

type extension struct {
	Publisher string `json:"publisher"`
	Name      string `json:"name"`
	Version   string `json:"version"`
}

func readExtension(container fspath.Path) (*extension, error) {
	content, err := os.ReadFile(container.Join("package.json").String())
	if err != nil {
		return nil, err
	}

	manifest := &extension{}
	if err := json.Unmarshal(content, manifest); err != nil {
		return nil, err
	}
	return manifest, nil
}

// findExtension looks for an installed extension; nil when there is none.
func findExtension(publisher string, name string) (*extension, error) {
	result, err := shell.Capture("code", []string{"--list-extensions", "--show-versions"}, shell.CaptureOptions{})
	if err != nil {
		return nil, err
	}

	for _, line := range strings.Split(result.Stdout, "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		identifier, version, _ := strings.Cut(line, "@")
		p, n, _ := strings.Cut(identifier, ".")
		if p == publisher && n == name {
			return &extension{Publisher: p, Name: n, Version: version}, nil
		}
	}
	return nil, nil
}
