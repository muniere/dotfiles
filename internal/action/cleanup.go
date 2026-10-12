package action

import (
	"fmt"
	"os"
	"sort"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/logging"
	"github.com/muniere/dotfiles/internal/platform"
	"github.com/muniere/dotfiles/internal/shell"
)

type CleanupContext struct {
	DryRun bool
	Logger *logging.Logger
}

func Cleanup(context CleanupContext) error {
	options := shell.Options{DryRun: context.DryRun, Logger: context.Logger}

	return sweep(books(platform.Identify()), true, options)
}

// sweep removes the broken symlinks under the destinations of the books.
// Destinations opted out of autoclean are scanned only when forced.
func sweep(books []*chef.CookBook, force bool, options shell.Options) error {
	// the progress line ends with "\r" so that the next line overwrites it
	progress := logging.Options{NoTerm: true}

	banner := "Scanning broken symlinks"
	options.Logger.Log(banner+"...\r", logging.LevelInfo, progress)

	specs := []*chef.PrefSpec{}
	for _, book := range books {
		specs = append(specs, book.Prefs...)
	}
	sort.SliceStable(specs, func(i, j int) bool {
		return specs[i].Dst.ExpandHome() < specs[j].Dst.ExpandHome()
	})

	found := []fspath.Path{}
	visited := map[fspath.Path]bool{}
	for _, spec := range specs {
		path := spec.Dst.ExpandHome()

		if visited[path] {
			continue
		}

		visited[path] = true

		if spec.Options.NoAutoclean && !force {
			options.Logger.Debugf("Skipping %s", path)
			continue
		}

		message := fmt.Sprintf("Scanning %s", path)
		options.Logger.Log(message+"...\r", logging.LevelDebug, progress)
		broken, err := scan(path)
		if err != nil {
			return err
		}
		found = append(found, broken...)
		options.Logger.Debugf("%s... Done", message)
	}

	options.Logger.Infof("%s... Done", banner)

	if len(found) > 0 {
		options.Logger.Infof("Found %d broken symlinks", len(found))
	} else {
		options.Logger.Infof("No broken symlinks were found")
	}

	for _, path := range found {
		if _, err := shell.Rm(path, options); err != nil {
			return err
		}
	}
	return nil
}

// scan lists the broken symlinks at the path or under it.
func scan(path fspath.Path) ([]fspath.Path, error) {
	lstat, err := path.Lstat()
	if err != nil {
		return nil, nil
	}
	if lstat.Mode()&os.ModeSymlink != 0 {
		if _, err := path.Stat(); err != nil {
			return []fspath.Path{path}, nil
		}
		return nil, nil
	}
	if !lstat.IsDir() {
		return nil, nil
	}

	entries, err := path.Walk()
	if err != nil {
		return nil, err
	}

	broken := []fspath.Path{}
	for _, entry := range entries {
		if !entry.IsSymlink {
			continue
		}
		if _, err := entry.Path.Stat(); err != nil {
			broken = append(broken, entry.Path)
		}
	}
	return broken, nil
}
