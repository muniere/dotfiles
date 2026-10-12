package action

import (
	"slices"

	"github.com/muniere/dotfiles/internal/logging"
	"github.com/muniere/dotfiles/internal/platform"
	"github.com/muniere/dotfiles/internal/shell"
)

type UnlinkContext struct {
	Cleanup    bool
	Deactivate bool
	DryRun     bool
	Logger     *logging.Logger
}

func Unlink(context UnlinkContext) error {
	options := shell.Options{DryRun: context.DryRun, Logger: context.Logger}

	target := platform.Identify()
	books := books(target)
	slices.Reverse(books)

	if context.Cleanup {
		if err := sweep(books, false, options); err != nil {
			return err
		}
	}

	for i, book := range books {
		context.Logger.Log(launched(i, books), logging.LevelMark, logging.Options{Bold: true})

		for _, spec := range book.Tmpls {
			if err := recallTmpl(spec, book.Container, options); err != nil {
				return err
			}
		}
		if context.Deactivate {
			if err := book.Deactivate.Call(options); err != nil {
				return err
			}
		}
		for _, spec := range book.Prefs {
			if err := unlinkPref(spec, book.Container, target, options); err != nil {
				return err
			}
		}
	}
	return nil
}
