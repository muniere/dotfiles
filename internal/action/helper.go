// Package action implements the commands: status, setup, link, unlink and cleanup.
package action

import (
	"errors"
	"fmt"
	"os"
	"strings"
	"text/template"
	"unicode"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/platform"
	"github.com/muniere/dotfiles/internal/shell"
	"github.com/muniere/dotfiles/vault"
)

// =====
// Books
// =====
var filter = fspath.NewFilter(nil, []string{
	"**/*.swp",
	"**/*.bak",
	"**/.DS_Store",
	"**/.keep",
	"**/.gitkeep",
})

func books(target platform.Platform) []*chef.CookBook {
	books := []*chef.CookBook{}
	for _, book := range vault.Books() {
		if book.Supports(target) {
			books = append(books, book)
		}
	}
	return books
}

func launched(index int, books []*chef.CookBook) string {
	return fmt.Sprintf("(%02d/%02d) %s Launched", index+1, len(books), books[index].Name)
}

// traverse pairs every file under the source with its destination.
// A source that does not exist yields nothing.
func traverse(specSrc fspath.Path, specDst fspath.Path, prefix fspath.Path) ([]chef.Bind, error) {
	src := specSrc.ExpandHome()
	if !specSrc.IsAbsolute() {
		src = fspath.New(prefix, specSrc.ExpandHome()).ToAbsolute()
	}

	dst := specDst.ExpandHome().ToAbsolute()

	stat, err := src.Stat()
	if err != nil {
		return nil, nil
	}

	if stat.Mode().IsRegular() {
		return []chef.Bind{{Src: src, Dst: dst}}, nil
	}

	entries, err := src.Walk()
	if err != nil {
		return nil, err
	}

	binds := []chef.Bind{}
	for _, entry := range entries {
		if !entry.IsFile {
			continue
		}
		binds = append(binds, chef.Bind{
			Src: entry.Path,
			Dst: fspath.New(dst, entry.Path.Relative(src)),
		})
	}
	return binds, nil
}

// =====
// Preferences
// =====
// inflatePref lists the files of the spec, the platform-specific ones first.
func inflatePref(spec *chef.PrefSpec, container fspath.Path, target platform.Platform) ([]chef.PrefChain, error) {
	prefixes := []fspath.Path{container.Join("default")}
	if target != platform.Default {
		prefixes = []fspath.Path{container.Join(fspath.Path(target)), container.Join("default")}
	}
	if spec.Src.IsAbsolute() {
		prefixes = []fspath.Path{""}
	}

	chains := []chef.PrefChain{}
	for _, prefix := range prefixes {
		binds, err := traverse(spec.Src, spec.Dst, prefix)
		if err != nil {
			return nil, err
		}
		for _, bind := range binds {
			chains = append(chains, spec.Chain(bind))
		}
	}
	return chains, nil
}

func linkPref(spec *chef.PrefSpec, container fspath.Path, target platform.Platform, options shell.Options) error {
	chains, err := inflatePref(spec, container, target)
	if err != nil {
		return err
	}

	for _, chain := range chains {
		if !filter.Test(chain.Src) {
			options.Logger.Debugf("File ignored: %s", chain.Src)
			continue
		}
		if _, err := chain.Src.Lstat(); err != nil {
			options.Logger.Infof("File not found: %s", chain.Src)
			continue
		}
		dstStat, err := chain.Dst.Lstat()
		if err == nil && dstStat.Mode()&os.ModeSymlink != 0 {
			options.Logger.Infof("Symlink already exists: %s", chain.Dst)
			continue
		}
		if err == nil && dstStat.Mode().IsRegular() {
			options.Logger.Infof("File already exists: %s", chain.Dst)
			continue
		}

		dir := chain.Dst.Dirname()
		if _, err := dir.Lstat(); err != nil {
			if _, err := shell.Mkdir(dir, shell.MkdirOptions{Options: options}); err != nil {
				return err
			}
		}

		switch chain.Options.Kind {
		case chef.PrefCopy:
			_, err = shell.Cp(chain.Src, chain.Dst, options)
		default:
			_, err = shell.Symlink(chain.Src, chain.Dst, options)
		}
		if err != nil {
			return err
		}
	}
	return nil
}

func unlinkPref(spec *chef.PrefSpec, container fspath.Path, target platform.Platform, options shell.Options) error {
	chains, err := inflatePref(spec, container, target)
	if err != nil {
		return err
	}

	for _, chain := range chains {
		if !filter.Test(chain.Src) {
			options.Logger.Debugf("File ignored: %s", chain.Src)
			continue
		}
		if _, err := chain.Src.Lstat(); err != nil {
			options.Logger.Infof("File not found: %s", chain.Src)
			continue
		}
		dstStat, err := chain.Dst.Lstat()
		if err != nil {
			options.Logger.Infof("File already removed: %s", chain.Dst)
			continue
		}
		if dstStat.Mode().IsRegular() {
			options.Logger.Infof("File is normal file: %s", chain.Dst)
			continue
		}

		if _, err := shell.Rm(chain.Dst, options); err != nil {
			return err
		}
	}
	return nil
}

// =====
// Templates
// =====
func inflateTmpl(spec *chef.TmplSpec, container fspath.Path) ([]chef.TmplChain, error) {
	prefix := container.Join("template")
	if spec.Src.IsAbsolute() {
		prefix = ""
	}

	binds, err := traverse(spec.Src, spec.Dst, prefix)
	if err != nil {
		return nil, err
	}

	chains := make([]chef.TmplChain, 0, len(binds))
	for _, bind := range binds {
		chains = append(chains, spec.Chain(bind))
	}
	return chains, nil
}

func renderTmpl(chain chef.TmplChain) (string, error) {
	source, err := os.ReadFile(chain.Src.String())
	if err != nil {
		return "", err
	}

	tmpl, err := template.New(chain.Src.String()).Option("missingkey=error").Parse(string(source))
	if err != nil {
		return "", err
	}

	var content strings.Builder
	if err := tmpl.Execute(&content, chain.Options.Values); err != nil {
		return "", err
	}
	return content.String(), nil
}

// forgeTmpl writes the rendered template into the file as a section,
// and leaves the rest of the file as it is.
func forgeTmpl(spec *chef.TmplSpec, container fspath.Path, options shell.Options) error {
	chains, err := inflateTmpl(spec, container)
	if err != nil {
		return err
	}

	for _, chain := range chains {
		content, err := renderTmpl(chain)
		if err != nil {
			return err
		}

		current := ""
		if stat, err := chain.Dst.Stat(); err == nil {
			if !stat.Mode().IsRegular() {
				options.Logger.Infof("File is not normal file: %s", chain.Dst)
				continue
			}
			bytes, err := os.ReadFile(chain.Dst.String())
			if err != nil {
				return err
			}
			current = string(bytes)
		}

		section := newSection(chain.Options.Comment)
		updated, err := section.put(current, content)
		if err != nil {
			return fmt.Errorf("%s: %w", chain.Dst, err)
		}
		if updated == current {
			options.Logger.Infof("Section is up-to-date: %s", chain.Dst)
			continue
		}

		if _, err := chain.Dst.Dirname().Stat(); err != nil {
			if _, err := shell.Mkdir(chain.Dst.Dirname(), shell.MkdirOptions{Options: options}); err != nil {
				return err
			}
		}

		options.Logger.Infof(
			"Write a section into %s with content:\n%s",
			chain.Dst, strings.TrimRightFunc(section.block(content), unicode.IsSpace),
		)

		if options.DryRun {
			continue
		}

		if err := os.WriteFile(chain.Dst.String(), []byte(updated), 0o666); err != nil {
			return err
		}
	}
	return nil
}

// recallTmpl removes the section from the file, and the file itself once nothing else is left.
func recallTmpl(spec *chef.TmplSpec, container fspath.Path, options shell.Options) error {
	chains, err := inflateTmpl(spec, container)
	if err != nil {
		return err
	}

	for _, chain := range chains {
		stat, err := chain.Dst.Stat()
		if err != nil {
			options.Logger.Infof("File not found: %s", chain.Dst)
			continue
		}
		if !stat.Mode().IsRegular() {
			options.Logger.Infof("File is not normal file: %s", chain.Dst)
			continue
		}

		content, err := renderTmpl(chain)
		if err != nil {
			return err
		}
		bytes, err := os.ReadFile(chain.Dst.String())
		if err != nil {
			return err
		}

		updated, dropped, err := newSection(chain.Options.Comment).drop(string(bytes), content)
		if err != nil {
			return fmt.Errorf("%s: %w", chain.Dst, err)
		}
		if !dropped {
			options.Logger.Infof("Section not found: %s", chain.Dst)
			continue
		}

		if strings.TrimSpace(updated) == "" {
			if _, err := shell.Rm(chain.Dst, options); err != nil {
				return err
			}
			continue
		}

		options.Logger.Infof("Remove a section from %s", chain.Dst)

		if options.DryRun {
			continue
		}

		if err := os.WriteFile(chain.Dst.String(), []byte(updated), 0o666); err != nil {
			return err
		}
	}
	return nil
}

// =====
// Sections
// =====
// section is the part of a file that this tool owns, enclosed by marker lines.
// The rest of the file belongs to the user and to the other tools writing there.
type section struct {
	// comment is the prefix of a comment line in the file.
	comment string
}

func newSection(comment string) section {
	if comment == "" {
		comment = "#"
	}
	return section{comment: comment}
}

func (s section) begin() string {
	return s.comment + " >>> muniere/dotfiles >>>"
}

func (s section) end() string {
	return s.comment + " <<< muniere/dotfiles <<<"
}

func (s section) block(content string) string {
	return s.begin() + "\n" + body(content) + "\n" + s.end() + "\n"
}

// put writes the content as the section, replacing the one the text already has.
// A text without a section gets one at the top, so that it comes before anything else.
func (s section) put(text string, content string) (string, error) {
	lines := strings.SplitAfter(text, "\n")

	begin, end, err := s.locate(lines)
	if err != nil {
		return "", err
	}
	if begin >= 0 {
		return strings.Join(lines[:begin], "") + s.block(content) + strings.Join(lines[end+1:], ""), nil
	}

	if start, stop := bare(text, content); start >= 0 {
		return text[:start] + s.block(content) + text[stop:], nil
	}

	if strings.TrimSpace(text) == "" {
		return s.block(content), nil
	}
	return s.block(content) + "\n" + text, nil
}

// drop removes the section, and tells whether there was one.
func (s section) drop(text string, content string) (string, bool, error) {
	lines := strings.SplitAfter(text, "\n")

	begin, end, err := s.locate(lines)
	if err != nil {
		return "", false, err
	}
	if begin >= 0 {
		before := strings.Join(lines[:begin], "")
		after := strings.Join(lines[end+1:], "")
		if before == "" {
			// the blank line that put leaves after a section at the top
			after = strings.TrimPrefix(after, "\n")
		}
		return before + after, true, nil
	}

	if start, stop := bare(text, content); start >= 0 {
		return text[:start] + text[stop:], true, nil
	}

	return text, false, nil
}

// locate tells the lines of the markers, or -1 for a text without a section.
func (s section) locate(lines []string) (int, int, error) {
	begin, end := -1, -1
	for i, line := range lines {
		switch strings.TrimRight(line, "\r\n") {
		case s.begin():
			if begin >= 0 {
				return -1, -1, errors.New("section begins twice")
			}
			begin = i
		case s.end():
			if end >= 0 {
				return -1, -1, errors.New("section ends twice")
			}
			end = i
		}
	}

	switch {
	case begin < 0 && end < 0:
		return -1, -1, nil
	case begin < 0:
		return -1, -1, errors.New("section ends without a beginning")
	case end < 0:
		return -1, -1, errors.New("section begins without an end")
	case end < begin:
		return -1, -1, errors.New("section ends before it begins")
	}
	return begin, end, nil
}

// bare finds the content written without markers, as the files created before the sections have it.
// It tells the range of whole lines, or -1 when the text does not have them.
func bare(text string, content string) (int, int) {
	body := body(content)
	if body == "" {
		return -1, -1
	}

	for offset := 0; ; {
		index := strings.Index(text[offset:], body)
		if index < 0 {
			return -1, -1
		}

		start := offset + index
		stop := start + len(body)
		offset = start + 1

		if start > 0 && text[start-1] != '\n' {
			continue
		}
		switch {
		case stop == len(text):
			return start, stop
		case text[stop] == '\n':
			return start, stop + 1
		}
	}
}

func body(content string) string {
	return strings.TrimRightFunc(content, unicode.IsSpace)
}
