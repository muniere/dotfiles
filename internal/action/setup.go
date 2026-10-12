package action

import (
	"github.com/muniere/dotfiles/internal/logging"
	"github.com/muniere/dotfiles/internal/platform"
	"github.com/muniere/dotfiles/internal/shell"
)

type SetupContext struct {
	DryRun bool
	Logger *logging.Logger
}

func Setup(context SetupContext) error {
	options := shell.Options{DryRun: context.DryRun, Logger: context.Logger}

	books := books(platform.Identify())

	for i, book := range books {
		context.Logger.Log(launched(i, books), logging.LevelMark, logging.Options{Bold: true})

		if err := book.Setup.Call(options); err != nil {
			return err
		}
	}
	return nil
}
