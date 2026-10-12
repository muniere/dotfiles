package action

import (
	"io"
	"os"
	"slices"
	"sort"
	"strings"

	"golang.org/x/term"

	"github.com/muniere/dotfiles/internal/ansi"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/platform"
)

type ColorMode string

const (
	ColorAuto   ColorMode = "auto"
	ColorAlways ColorMode = "always"
	ColorNever  ColorMode = "never"
)

type StatusContext struct {
	Long  bool
	Color ColorMode
	Out   *os.File
}

type statusLine struct {
	src fspath.Path
	dst fspath.Path
}

func Status(context StatusContext) error {
	target := platform.Identify()

	prefs := []statusLine{}
	tmpls := []statusLine{}
	for _, book := range books(target) {
		for _, spec := range book.Prefs {
			chains, err := inflatePref(spec, book.Container, target)
			if err != nil {
				return err
			}
			for _, chain := range chains {
				prefs = append(prefs, statusLine{src: chain.Src, dst: chain.Dst})
			}
		}
		for _, spec := range book.Tmpls {
			chains, err := inflateTmpl(spec, book.Container)
			if err != nil {
				return err
			}
			for _, chain := range chains {
				tmpls = append(tmpls, statusLine{src: chain.Src, dst: chain.Dst})
			}
		}
	}

	colored := context.colored()
	header := ansi.Styles(ansi.Yellow, ansi.Bold)

	sections := []string{
		formatSection(header("[[ Preferences ]]"), prefs, " -> ", context.Long, colored),
		formatSection(header("[[ Templates ]]"), tmpls, " <- ", context.Long, colored),
	}

	_, err := io.WriteString(context.Out, strings.Join(sections, "\n"))
	return err
}

func (c StatusContext) colored() bool {
	switch c.Color {
	case ColorAlways:
		return true
	case ColorNever:
		return false
	default:
		return term.IsTerminal(int(c.Out.Fd()))
	}
}

func formatSection(header string, lines []statusLine, separator string, long bool, colored bool) string {
	lines = slices.DeleteFunc(slices.Clone(lines), func(line statusLine) bool {
		return !filter.Test(line.src)
	})
	sort.SliceStable(lines, func(i, j int) bool {
		return lines[i].dst < lines[j].dst
	})

	texts := []string{header}
	for _, line := range lines {
		dst := line.dst.String()
		if colored {
			dst = decoration(line.dst)(dst)
		}
		if long {
			texts = append(texts, dst+separator+line.src.String())
		} else {
			texts = append(texts, dst)
		}
	}
	return strings.Join(texts, "\n") + "\n"
}

func decoration(path fspath.Path) ansi.Style {
	stat, err := path.Lstat()
	switch {
	case err != nil:
		return ansi.Red
	case stat.Mode()&os.ModeSymlink != 0:
		return ansi.Magenta
	case stat.IsDir():
		return ansi.Blue
	default:
		return ansi.Reset
	}
}
