// Package vi holds what the cook books of vim and nvim share.
package vi

import (
	"fmt"
	"strings"

	"github.com/muniere/dotfiles/internal/theme"
)

type ColorHighlight struct {
	Name       string
	Foreground *int
	Background *int
	Options    []string
}

type ColorAlias struct {
	Name string
	Link string
}

type ColorScheme struct {
	Name       string
	Palette    []string
	Highlights []ColorHighlight
	Aliases    []ColorAlias
}

func (s *ColorScheme) Render() string {
	lines := []string{fmt.Sprintf(`let g:colors_name="%s"`, s.Name), ""}

	for _, highlight := range s.Highlights {
		chunks := []string{"highlight", highlight.Name}

		if highlight.Foreground != nil {
			chunks = append(chunks, fmt.Sprintf("ctermfg=%d", *highlight.Foreground))

			if *highlight.Foreground < len(s.Palette) {
				chunks = append(chunks, fmt.Sprintf("guifg=%s", s.Palette[*highlight.Foreground]))
			}
		}
		if highlight.Background != nil {
			chunks = append(chunks, fmt.Sprintf("ctermbg=%d", *highlight.Background))

			if *highlight.Background < len(s.Palette) {
				chunks = append(chunks, fmt.Sprintf("guibg=%s", s.Palette[*highlight.Background]))
			}
		}
		if highlight.Options != nil {
			chunks = append(chunks, fmt.Sprintf("term=%s", strings.Join(highlight.Options, ",")))
		}

		lines = append(lines, strings.Join(chunks, " "))
	}

	for _, alias := range s.Aliases {
		chunks := []string{"highlight", "link", alias.Name, alias.Link}

		lines = append(lines, strings.Join(chunks, " "))
	}

	return strings.Join(lines, "\n")
}

func cterm(value int) *int {
	return &value
}

var Muniere = &ColorScheme{
	Name:    "muniere",
	Palette: theme.Palette[:],
	Highlights: []ColorHighlight{
		{Name: "SpecialKey", Foreground: cterm(4), Options: []string{"bold"}},
		{Name: "NonText", Foreground: cterm(12), Options: []string{"bold"}},
		{Name: "Directory", Foreground: cterm(4), Options: []string{"bold"}},
		{Name: "ErrorMsg", Foreground: cterm(15), Background: cterm(1), Options: []string{"standout"}},
		{Name: "IncSearch", Options: []string{"reverse"}},
		{Name: "Search", Background: cterm(11), Options: []string{"reverse"}},
		{Name: "MoreMsg", Foreground: cterm(2), Options: []string{"bold"}},
		{Name: "ModeMsg", Options: []string{"bold"}},
		{Name: "LineNr", Foreground: cterm(130)},
		{Name: "CursorLineNr", Foreground: cterm(130), Options: []string{"bold"}},
		{Name: "Question", Foreground: cterm(2), Options: []string{"standout"}},
		{Name: "StatusLine", Options: []string{"bold", "reverse"}},
		{Name: "StatusLineNC", Options: []string{"reverse"}},
		{Name: "VertSplit", Options: []string{"reverse"}},
		{Name: "Title", Foreground: cterm(5), Options: []string{"bold"}},
		{Name: "Visual", Background: cterm(7)},
		{Name: "VisualNOS", Options: []string{"bold", "underline"}},
		{Name: "WarningMsg", Foreground: cterm(1), Options: []string{"standout"}},
		{Name: "WildMenu", Foreground: cterm(0), Background: cterm(11), Options: []string{"standout"}},
		{Name: "Folded", Foreground: cterm(0), Background: cterm(15), Options: []string{"standout"}},
		{Name: "FoldColumn", Foreground: cterm(0), Background: cterm(15), Options: []string{"standout"}},
		{Name: "DiffAdd", Foreground: cterm(0), Background: cterm(2), Options: []string{"bold"}},
		{Name: "DiffChange", Foreground: cterm(0), Background: cterm(3), Options: []string{"bold"}},
		{Name: "DiffDelete", Foreground: cterm(0), Background: cterm(6), Options: []string{"bold"}},
		{Name: "DiffText", Foreground: cterm(0), Background: cterm(7), Options: []string{"reverse", "bold"}},
		{Name: "SignColumn", Background: cterm(0), Options: []string{"NONE"}},
		{Name: "Conceal", Foreground: cterm(7), Background: cterm(242)},
		{Name: "SpellBad", Background: cterm(224), Options: []string{"reverse"}},
		{Name: "SpellCap", Background: cterm(81), Options: []string{"reverse"}},
		{Name: "SpellRare", Background: cterm(225), Options: []string{"reverse"}},
		{Name: "SpellLocal", Background: cterm(14)},
		{Name: "Pmenu", Foreground: cterm(0), Background: cterm(225)},
		{Name: "PmenuSel", Foreground: cterm(0), Background: cterm(248)},
		{Name: "PmenuSbar", Background: cterm(248)},
		{Name: "PmenuThumb", Background: cterm(0)},
		{Name: "TabLine", Foreground: cterm(0), Background: cterm(7), Options: []string{"underline"}},
		{Name: "TabLineSel", Options: []string{"bold"}},
		{Name: "TabLineFill", Options: []string{"reverse"}},
		{Name: "CursorColumn", Background: cterm(7)},
		{Name: "CursorLine", Options: []string{"underline"}},
		{Name: "ColorColumn", Background: cterm(224), Options: []string{"reverse"}},
		{Name: "MatchParen", Foreground: cterm(0), Background: cterm(7), Options: []string{"reverse"}},
		{Name: "Comment", Foreground: cterm(4), Options: []string{"bold"}},
		{Name: "Constant", Foreground: cterm(1)},
		{Name: "Special", Foreground: cterm(5), Options: []string{"bold"}},
		{Name: "Identifier", Foreground: cterm(6)},
		{Name: "Statement", Foreground: cterm(130), Options: []string{"bold"}},
		{Name: "PreProc", Foreground: cterm(5)},
		{Name: "Type", Foreground: cterm(2)},
		{Name: "Underlined", Foreground: cterm(5), Options: []string{"underline"}},
		{Name: "Ignore", Foreground: cterm(15)},
		{Name: "Error", Foreground: cterm(15), Background: cterm(9), Options: []string{"reverse"}},
		{Name: "Todo", Foreground: cterm(0), Background: cterm(11), Options: []string{"standout"}},
	},
	Aliases: []ColorAlias{
		{Name: "Character", Link: "Constant"},
		{Name: "Number", Link: "Constant"},
		{Name: "Boolean", Link: "Constant"},
		{Name: "Float", Link: "Number"},
		{Name: "Function", Link: "Identifier"},
		{Name: "Conditional", Link: "Statement"},
		{Name: "Repeat", Link: "Statement"},
		{Name: "Label", Link: "Statement"},
		{Name: "Operator", Link: "Statement"},
		{Name: "Keyword", Link: "Statement"},
		{Name: "Exception", Link: "Statement"},
		{Name: "Include", Link: "PreProc"},
		{Name: "Define", Link: "PreProc"},
		{Name: "Macro", Link: "PreProc"},
		{Name: "PreCondit", Link: "PreProc"},
		{Name: "StorageClass", Link: "Type"},
		{Name: "Structure", Link: "Type"},
		{Name: "Typedef", Link: "Type"},
		{Name: "Tag", Link: "Special"},
		{Name: "SpecialChar", Link: "Special"},
		{Name: "Delimiter", Link: "Special"},
		{Name: "SpecialComment", Link: "Special"},
		{Name: "Debug", Link: "Special"},
	},
}
