package ansi

import (
	"fmt"
	"os"
	"strings"
)

type Style func(string) string

var (
	Reset   = style(0, 0)
	Bold    = style(1, 22)
	Red     = style(31, 39)
	Green   = style(32, 39)
	Yellow  = style(33, 39)
	Blue    = style(34, 39)
	Magenta = style(35, 39)
	Cyan    = style(36, 39)
	White   = style(37, 39)
)

func style(open int, close int) Style {
	opener := fmt.Sprintf("\x1b[%dm", open)
	closer := fmt.Sprintf("\x1b[%dm", close)
	return func(value string) string {
		if os.Getenv("NO_COLOR") != "" {
			return value
		}
		return opener + strings.ReplaceAll(value, closer, opener) + closer
	}
}

// Styles applies the styles in order, the first one innermost.
func Styles(styles ...Style) Style {
	return func(value string) string {
		for _, style := range styles {
			value = style(value)
		}
		return value
	}
}
