package androidstudio

import (
	"fmt"
	"os"
	"strings"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/idea"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/platform"
	"github.com/muniere/dotfiles/internal/shell"
	"github.com/muniere/dotfiles/internal/theme"
)

// AndroidStudioCookBook links the colors and keymaps into every installed version of the IDE.
var AndroidStudioCookBook = &chef.CookBook{
	Name:      "AndroidStudioCookBook",
	Container: layout.Vault().Join("AndroidStudio/"),
	Prefs: chef.GlobPrefs(chef.Bind{
		Src: ".",
		Dst: "~/Library/ApplicationSupport/Google/AndroidStudio*",
	}, []fspath.Path{"colors", "keymaps"}),
	// Activate rewrites the terminal colors of the color scheme with the palette.
	Activate: func(options shell.Options) error {
		path := layout.Vault().Join("AndroidStudio", "darwin/colors/Monokai.icls")

		content, err := os.ReadFile(path.String())
		if err != nil {
			return err
		}
		source := string(content)

		scheme, err := idea.ParseColorScheme(source)
		if err != nil {
			return fmt.Errorf("%s: %w", path, err)
		}
		scheme.ApplyDefaults(map[string]string{
			"BLOCK_TERMINAL_DEFAULT_FOREGROUND": theme.Palette[7],
		})
		scheme.ApplyAttributes(map[string]string{
			"BLOCK_TERMINAL_BLACK":          theme.Palette[0],
			"BLOCK_TERMINAL_RED":            theme.Palette[1],
			"BLOCK_TERMINAL_GREEN":          theme.Palette[2],
			"BLOCK_TERMINAL_YELLOW":         theme.Palette[3],
			"BLOCK_TERMINAL_BLUE":           theme.Palette[4],
			"BLOCK_TERMINAL_MAGENTA":        theme.Palette[5],
			"BLOCK_TERMINAL_CYAN":           theme.Palette[6],
			"BLOCK_TERMINAL_WHITE":          theme.Palette[7],
			"BLOCK_TERMINAL_BLACK_BRIGHT":   theme.Palette[8],
			"BLOCK_TERMINAL_RED_BRIGHT":     theme.Palette[9],
			"BLOCK_TERMINAL_GREEN_BRIGHT":   theme.Palette[10],
			"BLOCK_TERMINAL_YELLOW_BRIGHT":  theme.Palette[11],
			"BLOCK_TERMINAL_BLUE_BRIGHT":    theme.Palette[12],
			"BLOCK_TERMINAL_MAGENTA_BRIGHT": theme.Palette[13],
			"BLOCK_TERMINAL_CYAN_BRIGHT":    theme.Palette[14],
			"BLOCK_TERMINAL_WHITE_BRIGHT":   theme.Palette[15],
			"CONSOLE_BLACK_OUTPUT":          theme.Palette[0],
			"CONSOLE_RED_OUTPUT":            theme.Palette[1],
			"CONSOLE_GREEN_OUTPUT":          theme.Palette[2],
			"CONSOLE_YELLOW_OUTPUT":         theme.Palette[3],
			"CONSOLE_BLUE_OUTPUT":           theme.Palette[4],
			"CONSOLE_MAGENTA_OUTPUT":        theme.Palette[5],
			"CONSOLE_CYAN_OUTPUT":           theme.Palette[6],
			"CONSOLE_WHITE_OUTPUT":          theme.Palette[7],
		})

		result := scheme.Build(strings.HasSuffix(source, "\n"))

		if source == result {
			options.Logger.Infof("Color scheme is up-to-date: %s", path)
			return nil
		}

		options.Logger.Infof("Color scheme is outdated. Now update: %s", path)
		if options.DryRun {
			return nil
		}

		return os.WriteFile(path.String(), []byte(result), 0o666)
	},
	Platforms: []platform.Platform{platform.Darwin},
}
