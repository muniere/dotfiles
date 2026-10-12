package fspath

import (
	"os"
	"path"
	"path/filepath"
	"regexp"
	"slices"
	"strings"
)

// Path keeps a trailing slash on purpose: "~/.config/tmux/" and "~/.config/tmux"
// are distinct values.
type Path string

func New(values ...Path) Path {
	parts := make([]string, 0, len(values))
	for _, value := range values {
		if value != "" {
			parts = append(parts, string(value))
		}
	}
	if len(parts) == 0 {
		return "."
	}
	return Path(normalize(strings.Join(parts, "/")))
}

func normalize(value string) string {
	cleaned := path.Clean(value)
	if strings.HasSuffix(value, "/") && !strings.HasSuffix(cleaned, "/") {
		return cleaned + "/"
	}
	return cleaned
}

func (p Path) IsAbsolute() bool {
	return path.IsAbs(string(p))
}

func (p Path) ToAbsolute() Path {
	if p.IsAbsolute() {
		return New(p)
	}
	abs, err := filepath.Abs(string(p))
	if err != nil {
		return New(p)
	}
	return New(Path(abs))
}

func (p Path) Stat() (os.FileInfo, error) {
	return os.Stat(string(p))
}

func (p Path) Lstat() (os.FileInfo, error) {
	return os.Lstat(string(p))
}

type WalkEntry struct {
	Path      Path
	IsFile    bool
	IsDir     bool
	IsSymlink bool
}

// Walk lists the entries under the path recursively, starting with the path itself.
// Symlinks are reported but not followed, except for the root.
// Entries come in directory order, not sorted.
func (p Path) Walk() ([]WalkEntry, error) {
	info, err := p.Stat()
	if err != nil {
		return nil, err
	}
	entries := []WalkEntry{{
		Path:   New(p),
		IsFile: info.Mode().IsRegular(),
		IsDir:  info.IsDir(),
	}}
	return walk(p, entries)
}

func walk(root Path, entries []WalkEntry) ([]WalkEntry, error) {
	children, err := readDir(root)
	if err != nil {
		return nil, err
	}
	for _, child := range children {
		path := root.Join(Path(child.Name()))
		switch {
		case child.Type()&os.ModeSymlink != 0:
			entries = append(entries, WalkEntry{Path: path, IsSymlink: true})
		case child.IsDir():
			entries = append(entries, WalkEntry{Path: path, IsDir: true})
			entries, err = walk(path, entries)
			if err != nil {
				return nil, err
			}
		default:
			entries = append(entries, WalkEntry{Path: path, IsFile: child.Type().IsRegular()})
		}
	}
	return entries, nil
}

func readDir(dir Path) ([]os.DirEntry, error) {
	file, err := os.Open(string(dir))
	if err != nil {
		return nil, err
	}
	defer file.Close()
	return file.ReadDir(-1)
}

func (p Path) Dirname() Path {
	trimmed := strings.TrimRight(string(p), "/")
	if trimmed == "" {
		return New(Path(path.Dir(string(p))))
	}
	return New(Path(path.Dir(trimmed)))
}

// Relative returns the path as seen from the other path.
func (p Path) Relative(other Path) Path {
	rel, err := filepath.Rel(string(other.ToAbsolute()), string(p.ToAbsolute()))
	if err != nil {
		return New(p)
	}
	return New(Path(rel))
}

func (p Path) Join(others ...Path) Path {
	return New(append([]Path{p}, others...)...)
}

func (p Path) ExpandHome() Path {
	home := os.Getenv("HOME")
	if home == "" {
		return p
	}
	if strings.HasPrefix(string(p), "~") {
		return New(Path(home + string(p)[1:]))
	}
	return New(p)
}

func (p Path) TransHome() Path {
	home := os.Getenv("HOME")
	if home == "" {
		return p
	}
	return New(Path(strings.Replace(string(p), home, "$HOME", 1)))
}

func (p Path) String() string {
	return string(p)
}

// ExpandGlob lists the paths matching the pattern, sorted.
func ExpandGlob(pattern Path) ([]Path, error) {
	value := string(pattern)
	matches := []Path{"."}
	if strings.HasPrefix(value, "/") {
		matches = []Path{"/"}
	}

	for _, segment := range strings.Split(value, "/") {
		if segment == "" {
			continue
		}

		next := []Path{}
		for _, base := range matches {
			if !strings.ContainsAny(segment, "*?[") {
				candidate := base.Join(Path(segment))
				if _, err := candidate.Stat(); err == nil {
					next = append(next, candidate)
				}
				continue
			}

			children, err := readDir(base)
			if err != nil {
				continue
			}
			for _, child := range children {
				ok, err := path.Match(segment, child.Name())
				if err != nil {
					return nil, err
				}
				if ok {
					next = append(next, base.Join(Path(child.Name())))
				}
			}
		}
		slices.Sort(next)
		matches = next
	}

	return matches, nil
}

type Filter struct {
	whitelist []*regexp.Regexp
	blacklist []*regexp.Regexp
}

func NewFilter(whitelist []string, blacklist []string) *Filter {
	filter := &Filter{}
	for _, glob := range whitelist {
		filter.whitelist = append(filter.whitelist, globToRegexp(glob))
	}
	for _, glob := range blacklist {
		filter.blacklist = append(filter.blacklist, globToRegexp(glob))
	}
	return filter
}

func (f *Filter) Test(path Path) bool {
	for _, re := range f.whitelist {
		if re.MatchString(string(path)) {
			return true
		}
	}
	for _, re := range f.blacklist {
		if re.MatchString(string(path)) {
			return false
		}
	}
	return true
}

// globToRegexp supports "**/", "*" and "?" only, which is all the filters need.
func globToRegexp(glob string) *regexp.Regexp {
	var b strings.Builder
	b.WriteString("^")
	for i := 0; i < len(glob); {
		switch {
		case strings.HasPrefix(glob[i:], "**/"):
			b.WriteString(`(?:[^/]*(?:/|$)+)*`)
			i += 3
		case glob[i] == '*':
			b.WriteString(`[^/]*`)
			i++
		case glob[i] == '?':
			b.WriteString(`[^/]`)
			i++
		default:
			b.WriteString(regexp.QuoteMeta(glob[i : i+1]))
			i++
		}
	}
	b.WriteString("/*$")
	return regexp.MustCompile(b.String())
}
