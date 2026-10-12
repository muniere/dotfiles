package action

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/shell"
)

func TestTmplRoundTrip(t *testing.T) {
	dir := t.TempDir()
	src := filepath.Join(dir, "template")
	dst := filepath.Join(dir, "home", "profile")

	if err := os.WriteFile(src, []byte(`export A="{{ .a }}"`+"\n"), 0o666); err != nil {
		t.Fatal(err)
	}
	spec := chef.Tmpl(
		chef.Bind{Src: fspath.Path(src), Dst: fspath.Path(dst)},
		chef.TmplOptions{Values: map[string]any{"a": "1"}},
	)

	block := "# >>> muniere/dotfiles >>>\nexport A=\"1\"\n# <<< muniere/dotfiles <<<\n"
	docker := "# added by Docker Desktop\n"

	read := func() string {
		content, err := os.ReadFile(dst)
		if err != nil {
			t.Fatal(err)
		}
		return string(content)
	}
	forge := func(options shell.Options) {
		if err := forgeTmpl(spec, "", options); err != nil {
			t.Fatal(err)
		}
	}
	recall := func(options shell.Options) {
		if err := recallTmpl(spec, "", options); err != nil {
			t.Fatal(err)
		}
	}

	// nothing gets written on a dry run
	forge(shell.Options{DryRun: true})
	if _, err := os.Stat(dst); err == nil {
		t.Fatalf("dry run created %s", dst)
	}

	// link creates the file, and linking again changes nothing
	forge(shell.Options{})
	forge(shell.Options{})
	if got := read(); got != block {
		t.Fatalf("after link: %q, want %q", got, block)
	}

	// what the others append survives a relink
	if err := os.WriteFile(dst, []byte(block+docker), 0o666); err != nil {
		t.Fatal(err)
	}
	recall(shell.Options{DryRun: true})
	if got := read(); got != block+docker {
		t.Fatalf("dry run changed the file: %q", got)
	}
	recall(shell.Options{})
	if got := read(); got != docker {
		t.Fatalf("after unlink: %q, want %q", got, docker)
	}
	recall(shell.Options{})
	forge(shell.Options{})
	if got, want := read(), block+"\n"+docker; got != want {
		t.Fatalf("after relink: %q, want %q", got, want)
	}

	// the file goes away once nothing but the section is left
	if err := os.WriteFile(dst, []byte(block), 0o666); err != nil {
		t.Fatal(err)
	}
	recall(shell.Options{})
	if _, err := os.Stat(dst); err == nil {
		t.Fatalf("unlink left %s", dst)
	}
}

const (
	testBlock   = "# >>> muniere/dotfiles >>>\nexport A=1\nexport B=2\n# <<< muniere/dotfiles <<<\n"
	testContent = "export A=1\nexport B=2\n"
	testDocker  = "# added by Docker Desktop\nexport PATH=\"$PATH:/docker\"\n"
)

func TestSectionPut(t *testing.T) {
	cases := []struct {
		name string
		text string
		want string
	}{
		{name: "empty", text: "", want: testBlock},
		{name: "blank", text: "\n", want: testBlock},
		{name: "up-to-date", text: testBlock, want: testBlock},
		{name: "outdated", text: "# >>> muniere/dotfiles >>>\nexport A=0\n# <<< muniere/dotfiles <<<\n", want: testBlock},
		{name: "prepend", text: testDocker, want: testBlock + "\n" + testDocker},
		{name: "keep around", text: testDocker + testBlock + "alias l=ls\n", want: testDocker + testBlock + "alias l=ls\n"},
		{name: "bare", text: testContent, want: testBlock},
		{name: "bare without newline", text: "export A=1\nexport B=2", want: testBlock},
		{name: "bare after others", text: testDocker + "\n" + testContent, want: testDocker + "\n" + testBlock},
		{name: "bare before others", text: testContent + "\n" + testDocker, want: testBlock + "\n" + testDocker},
		{name: "not whole lines", text: "export A=1\nexport B=22\n", want: testBlock + "\n" + "export A=1\nexport B=22\n"},
	}
	for _, c := range cases {
		got, err := newSection("").put(c.text, testContent)
		if err != nil {
			t.Errorf("%s: %v", c.name, err)
			continue
		}
		if got != c.want {
			t.Errorf("%s: put = %q, want %q", c.name, got, c.want)
		}
	}
}

func TestSectionDrop(t *testing.T) {
	cases := []struct {
		name    string
		text    string
		want    string
		dropped bool
	}{
		{name: "only", text: testBlock, want: "", dropped: true},
		{name: "prepended", text: testBlock + "\n" + testDocker, want: testDocker, dropped: true},
		{name: "keep around", text: testDocker + testBlock + "alias l=ls\n", want: testDocker + "alias l=ls\n", dropped: true},
		{name: "outdated", text: "# >>> muniere/dotfiles >>>\nexport A=0\n# <<< muniere/dotfiles <<<\n", want: "", dropped: true},
		{name: "bare", text: testContent, want: "", dropped: true},
		{name: "bare after others", text: testDocker + "\n" + testContent, want: testDocker + "\n", dropped: true},
		{name: "nothing", text: testDocker, want: testDocker, dropped: false},
		{name: "empty", text: "", want: "", dropped: false},
	}
	for _, c := range cases {
		got, dropped, err := newSection("").drop(c.text, testContent)
		if err != nil {
			t.Errorf("%s: %v", c.name, err)
			continue
		}
		if got != c.want || dropped != c.dropped {
			t.Errorf("%s: drop = %q, %t, want %q, %t", c.name, got, dropped, c.want, c.dropped)
		}
	}
}

func TestSectionBroken(t *testing.T) {
	cases := []string{
		"# >>> muniere/dotfiles >>>\nexport A=1\n",
		"export A=1\n# <<< muniere/dotfiles <<<\n",
		"# <<< muniere/dotfiles <<<\n# >>> muniere/dotfiles >>>\n",
		testBlock + testBlock,
	}
	for _, text := range cases {
		if _, err := newSection("").put(text, testContent); err == nil {
			t.Errorf("put(%q): no error", text)
		}
		if _, _, err := newSection("").drop(text, testContent); err == nil {
			t.Errorf("drop(%q): no error", text)
		}
	}
}

func TestSectionComment(t *testing.T) {
	got, err := newSection(`"`).put("", "source x\n")
	want := "\" >>> muniere/dotfiles >>>\nsource x\n\" <<< muniere/dotfiles <<<\n"
	if err != nil || got != want {
		t.Errorf("put = %q, %v, want %q", got, err, want)
	}
}
