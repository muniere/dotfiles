package main

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"

	"github.com/muniere/dotfiles/internal/action"
	"github.com/muniere/dotfiles/internal/logging"
)

func main() {
	root := &cobra.Command{
		Use:           "dotfiles",
		Short:         "Link the files in the vault into the home directory",
		SilenceUsage:  true,
		SilenceErrors: true,
		Args:          cobra.NoArgs,
		RunE: func(command *cobra.Command, _ []string) error {
			command.Help()
			os.Exit(1)
			return nil
		},
	}
	root.CompletionOptions.DisableDefaultCmd = true

	root.AddCommand(
		statusCommand(),
		setupCommand(),
		linkCommand(),
		unlinkCommand(),
		relinkCommand(),
		cleanupCommand(),
	)

	if err := root.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "error: %s\n", err)
		os.Exit(1)
	}
}

// runFlags are the flags shared by the commands that change files.
type runFlags struct {
	dryRun  bool
	verbose bool
}

func (f *runFlags) register(command *cobra.Command) {
	command.Flags().BoolVarP(&f.dryRun, "dry-run", "n", false, "Do not execute commands actually")
	command.Flags().BoolVarP(&f.verbose, "verbose", "v", false, "Show verbose messages")
}

func (f *runFlags) logger() *logging.Logger {
	if f.verbose {
		return logging.New(logging.LevelDebug)
	}
	return logging.New(logging.LevelTrace)
}

func statusCommand() *cobra.Command {
	var long bool
	var color string

	command := &cobra.Command{
		Use:   "status",
		Short: "Show link status",
		Args:  cobra.NoArgs,
		RunE: func(_ *cobra.Command, _ []string) error {
			mode := action.ColorMode(color)
			switch mode {
			case action.ColorAuto, action.ColorAlways, action.ColorNever:
			default:
				return fmt.Errorf("invalid value for --color: %s", color)
			}

			return action.Status(action.StatusContext{
				Long:  long,
				Color: mode,
				Out:   os.Stdout,
			})
		},
	}

	command.Flags().BoolVarP(&long, "long", "l", false, "Show in long format")
	command.Flags().StringVar(&color, "color", "auto", "Choose colorize style (auto, always, never)")

	return command
}

func setupCommand() *cobra.Command {
	var flags runFlags

	command := &cobra.Command{
		Use:   "setup",
		Short: "Setup files for link",
		Args:  cobra.NoArgs,
		RunE: func(_ *cobra.Command, _ []string) error {
			return action.Setup(action.SetupContext{
				DryRun: flags.dryRun,
				Logger: flags.logger(),
			})
		},
	}

	flags.register(command)

	return command
}

func linkCommand() *cobra.Command {
	var flags runFlags
	var noCleanup, noSetup, noActivate bool

	command := &cobra.Command{
		Use:   "link",
		Short: "Link files",
		Args:  cobra.NoArgs,
		RunE: func(_ *cobra.Command, _ []string) error {
			return action.Link(action.LinkContext{
				Cleanup:  !noCleanup,
				Setup:    !noSetup,
				Activate: !noActivate,
				DryRun:   flags.dryRun,
				Logger:   flags.logger(),
			})
		},
	}

	command.Flags().BoolVar(&noCleanup, "no-cleanup", false, "Skip cleanup action before link")
	command.Flags().BoolVar(&noSetup, "no-setup", false, "Skip setup before link")
	command.Flags().BoolVar(&noActivate, "no-activate", false, "Skip activation after each link")
	flags.register(command)

	return command
}

func unlinkCommand() *cobra.Command {
	var flags runFlags
	var noCleanup, noDeactivate bool

	command := &cobra.Command{
		Use:   "unlink",
		Short: "Unlink files",
		Args:  cobra.NoArgs,
		RunE: func(_ *cobra.Command, _ []string) error {
			return action.Unlink(action.UnlinkContext{
				Cleanup:    !noCleanup,
				Deactivate: !noDeactivate,
				DryRun:     flags.dryRun,
				Logger:     flags.logger(),
			})
		},
	}

	command.Flags().BoolVar(&noCleanup, "no-cleanup", false, "Skip cleanup action before unlink")
	command.Flags().BoolVar(&noDeactivate, "no-deactivate", false, "Skip deactivation after each unlink")
	flags.register(command)

	return command
}

func relinkCommand() *cobra.Command {
	var flags runFlags

	command := &cobra.Command{
		Use:   "relink",
		Short: "Unlink files, then link them again",
		Args:  cobra.NoArgs,
		RunE: func(_ *cobra.Command, _ []string) error {
			logger := flags.logger()

			err := action.Unlink(action.UnlinkContext{
				Cleanup:    true,
				Deactivate: true,
				DryRun:     flags.dryRun,
				Logger:     logger,
			})
			if err != nil {
				return err
			}

			return action.Link(action.LinkContext{
				Cleanup:  true,
				Setup:    true,
				Activate: true,
				DryRun:   flags.dryRun,
				Logger:   logger,
			})
		},
	}

	flags.register(command)

	return command
}

func cleanupCommand() *cobra.Command {
	var flags runFlags

	command := &cobra.Command{
		Use:   "cleanup",
		Short: "Cleanup broken links",
		Args:  cobra.NoArgs,
		RunE: func(_ *cobra.Command, _ []string) error {
			return action.Cleanup(action.CleanupContext{
				DryRun: flags.dryRun,
				Logger: flags.logger(),
			})
		},
	}

	flags.register(command)

	return command
}
