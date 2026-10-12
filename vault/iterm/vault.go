package iterm

import (
	"fmt"
	"math"
	"strconv"
	"strings"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/platform"
	"github.com/muniere/dotfiles/internal/plist"
	"github.com/muniere/dotfiles/internal/shell"
	"github.com/muniere/dotfiles/internal/theme"
)

var ITermCookBook = &chef.CookBook{
	Name:      "iTermCookBook",
	Container: layout.Vault().Join("iterm/"),
	Activate: func(options shell.Options) error {
		path := fspath.Path("~/Library/Preferences/com.googlecode.iterm2.plist").ExpandHome()

		if _, err := path.Lstat(); err != nil {
			options.Logger.Infof("iTerm 2 not installed yet. skip.")
			return nil
		}

		// for default profile
		defaults := &plist.List{
			Path: path.ExpandHome(),
			Root: "New Bookmarks:0",
		}

		profile, err := defaults.GetDict("")
		if err != nil {
			return err
		}
		if profile == nil {
			options.Logger.Infof("iTerm 2 profile not found. skip.")
			return nil
		}

		booleans := []struct {
			key   string
			value bool
			label string
		}{
			{key: "Use Non-ASCII Font", value: true, label: "Non-ASCII Font already enabled"},
			{key: "Use Separate Colors for Light and Dark Mode", value: false, label: "Separate Colors already disabled"},
			{key: "Brighten Bold Text", value: true, label: "Brighten Bold Text already enabled"},
			{key: "Bright Bold", value: true, label: "Bright Bold already enabled"},
		}

		setBoolean := func(index int) error {
			pref := booleans[index]
			if profile.Get(pref.key) == pref.value {
				options.Logger.Infof("%s: %t", pref.label, pref.value)
				return nil
			}
			_, err := defaults.SetBoolean(pref.key, pref.value, options)
			return err
		}

		if err := setBoolean(0); err != nil {
			return err
		}

		{
			key := "Non Ascii Font"
			value := "HackNFM-Regular 11"

			if profile.Get(key) == value {
				options.Logger.Infof("Nerd Font already configured: %s", value)
			} else if _, err := defaults.SetString(key, value, options); err != nil {
				return err
			}
		}

		for index := 1; index < len(booleans); index++ {
			if err := setBoolean(index); err != nil {
				return err
			}
		}

		for i := 0; i < 16; i++ {
			entry := fmt.Sprintf("Ansi %d Color", i)

			components, _ := profile.Get(entry).(*plist.Dict)
			preferences := []struct {
				field string
				value float64
			}{
				{field: "Red Component", value: colorComponent(theme.Palette[i][1:3])},
				{field: "Green Component", value: colorComponent(theme.Palette[i][3:5])},
				{field: "Blue Component", value: colorComponent(theme.Palette[i][5:7])},
			}

			type match struct {
				field string
				value float64
			}
			matches := []match{}
			for _, pref := range preferences {
				property, ok := components.Get(pref.field).(float64)
				if ok && math.Abs(property-pref.value) < 1.0/255 {
					matches = append(matches, match{field: pref.field, value: property})
				} else if _, err := defaults.SetReal(entry+":"+pref.field, pref.value, options); err != nil {
					return err
				}
			}

			if len(matches) == len(preferences) {
				values := []string{}
				for _, m := range matches {
					values = append(values, plist.FormatNumber(m.value))
				}
				options.Logger.Infof("%s already configured: [%s]", entry, strings.Join(values, ", "))
			} else {
				for _, m := range matches {
					options.Logger.Infof("%s (%s) already configured: %s", entry, m.field, plist.FormatNumber(m.value))
				}
			}
		}

		for _, entry := range profile.Entries {
			if strings.Contains(entry.Key, "(Light)") || strings.Contains(entry.Key, "(Dark)") {
				if _, err := defaults.Remove(entry.Key, options); err != nil {
					return err
				}
			}
		}

		// for global
		global := &plist.List{
			Path: path,
			Root: "GlobalKeyMap",
		}

		{
			bindings := []struct {
				shortcutLabel string
				shortcutValue string
				actionLabel   string
				actionValue   int
				attributes    []plist.Entry
			}{
				{
					shortcutLabel: "⌘Return↵",
					shortcutValue: "0xd-0x100000-0x24",
					actionLabel:   "Ignore",
					actionValue:   13,
					attributes: []plist.Entry{
						{Key: "Apply Mode", Value: 0},
						{Key: "Escaping", Value: 2},
						{Key: "Text", Value: ""},
						{Key: "Version", Value: 2},
					},
				},
			}

			for _, binding := range bindings {
				current, err := global.GetDict(binding.shortcutValue)
				if err != nil {
					return err
				}
				if current != nil && current.Get("Action") == float64(binding.actionValue) {
					options.Logger.Infof("Binding for %s already configured: %s", binding.shortcutLabel, binding.actionLabel)
					continue
				}

				attrs := append(
					[]plist.Entry{{Key: "Action", Value: binding.actionValue}},
					binding.attributes...,
				)
				if _, err := global.SetDict(binding.shortcutValue, attrs, options); err != nil {
					return err
				}
				options.Logger.Infof("Set binding for %s to %s", binding.shortcutLabel, binding.actionLabel)
			}
		}
		return nil
	},
	Platforms: []platform.Platform{platform.Darwin},
}

// colorComponent turns a two-digit hex into a color component between 0 and 1.
func colorComponent(hex string) float64 {
	value, _ := strconv.ParseInt(hex, 16, 64)
	return float64(value) / 255
}
