// Package chef defines how the files of a tool get installed.
package chef

import (
	"slices"

	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/platform"
	"github.com/muniere/dotfiles/internal/shell"
)

type Bind struct {
	Src fspath.Path
	Dst fspath.Path
}

// =====
// Preferences
// =====
type PrefKind string

const (
	PrefLink PrefKind = "link"
	PrefCopy PrefKind = "copy"
)

type PrefOptions struct {
	Kind        PrefKind
	NoAutoclean bool
}

// PrefSpec tells to link or copy the files under Src to Dst.
type PrefSpec struct {
	Src     fspath.Path
	Dst     fspath.Path
	Options PrefOptions
}

// PrefChain is a single file of a PrefSpec.
type PrefChain struct {
	Src     fspath.Path
	Dst     fspath.Path
	Options PrefOptions
}

func Pref(bind Bind, options ...PrefOptions) *PrefSpec {
	spec := &PrefSpec{
		Src: fspath.New(bind.Src),
		Dst: fspath.New(bind.Dst),
	}
	if len(options) > 0 {
		spec.Options = options[0]
	}
	return spec
}

// GlobPrefs makes specs for each child under every destination matching the glob.
func GlobPrefs(bind Bind, children []fspath.Path, options ...PrefOptions) []*PrefSpec {
	matches, err := fspath.ExpandGlob(bind.Dst.ExpandHome())
	if err != nil {
		panic(err)
	}

	specs := []*PrefSpec{}
	for _, match := range matches {
		for _, child := range children {
			specs = append(specs, Pref(Bind{
				Src: fspath.New(bind.Src, child),
				Dst: fspath.New(match, child).ExpandHome(),
			}, options...))
		}
	}
	return specs
}

func (s *PrefSpec) Chain(bind Bind) PrefChain {
	return PrefChain{Src: fspath.New(bind.Src), Dst: fspath.New(bind.Dst), Options: s.Options}
}

// =====
// Templates
// =====
type TmplOptions struct {
	Values map[string]any
	// Comment is the prefix of a comment line in the file, which is "#" unless given.
	Comment string
}

// TmplSpec tells to keep the template at Src, once rendered, as a section of Dst.
type TmplSpec struct {
	Src     fspath.Path
	Dst     fspath.Path
	Options TmplOptions
}

// TmplChain is a single file of a TmplSpec.
type TmplChain struct {
	Src     fspath.Path
	Dst     fspath.Path
	Options TmplOptions
}

func Tmpl(bind Bind, options ...TmplOptions) *TmplSpec {
	spec := &TmplSpec{
		Src: fspath.New(bind.Src),
		Dst: fspath.New(bind.Dst),
	}
	if len(options) > 0 {
		spec.Options = options[0]
	}
	return spec
}

func (s *TmplSpec) Chain(bind Bind) TmplChain {
	return TmplChain{Src: fspath.New(bind.Src), Dst: fspath.New(bind.Dst), Options: s.Options}
}

// =====
// CookBook
// =====
type Callback func(options shell.Options) error

// Call does nothing for a nil callback.
func (fn Callback) Call(options shell.Options) error {
	if fn == nil {
		return nil
	}
	return fn(options)
}

type CookBook struct {
	Name       string
	Container  fspath.Path
	Prefs      []*PrefSpec
	Tmpls      []*TmplSpec
	Platforms  []platform.Platform
	Setup      Callback
	Activate   Callback
	Deactivate Callback
}

func (b *CookBook) Supports(target platform.Platform) bool {
	return b.Platforms == nil || slices.Contains(b.Platforms, target)
}
