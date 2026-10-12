package action

import (
	"github.com/muniere/dotfiles/internal/logging"
	"github.com/muniere/dotfiles/internal/platform"
	"github.com/muniere/dotfiles/internal/shell"
)

type LinkContext struct {
	Cleanup  bool
	Setup    bool
	Activate bool
	DryRun   bool
	Logger   *logging.Logger
}

func Link(context LinkContext) error {
	options := shell.Options{DryRun: context.DryRun, Logger: context.Logger}

	target := platform.Identify()
	books := books(target)

	if context.Cleanup {
		if err := sweep(books, false, options); err != nil {
			return err
		}
	}

	for i, book := range books {
		context.Logger.Log(launched(i, books), logging.LevelMark, logging.Options{Bold: true})

		if context.Setup {
			if err := book.Setup.Call(options); err != nil {
				return err
			}
		}

		for _, spec := range book.Prefs {
			if err := linkPref(spec, book.Container, target, options); err != nil {
				return err
			}
		}
		if context.Activate {
			if err := book.Activate.Call(options); err != nil {
				return err
			}
		}
		for _, spec := range book.Tmpls {
			if err := forgeTmpl(spec, book.Container, options); err != nil {
				return err
			}
		}
	}
	return nil
}
