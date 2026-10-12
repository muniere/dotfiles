package fspath

import "testing"

func TestNew(t *testing.T) {
	cases := []struct {
		values []Path
		want   Path
	}{
		{values: nil, want: "."},
		{values: []Path{"./vault"}, want: "vault"},
		{values: []Path{"vault", "tmux/"}, want: "vault/tmux/"},
		{values: []Path{"vault/tmux/", "default"}, want: "vault/tmux/default"},
		{values: []Path{"vault/tmux/default", "."}, want: "vault/tmux/default"},
		{values: []Path{"/home/.config/tmux/", "tmux.conf"}, want: "/home/.config/tmux/tmux.conf"},
		{values: []Path{"a//b/../c/"}, want: "a/c/"},
		{values: []Path{"/"}, want: "/"},
	}
	for _, c := range cases {
		if got := New(c.values...); got != c.want {
			t.Errorf("New(%q) = %q, want %q", c.values, got, c.want)
		}
	}
}

func TestDirname(t *testing.T) {
	cases := map[Path]Path{
		"/a/b/c.txt": "/a/b",
		"/a/b/":      "/a",
		"/a":         "/",
		"/":          "/",
		"a":          ".",
	}
	for path, want := range cases {
		if got := path.Dirname(); got != want {
			t.Errorf("%q.Dirname() = %q, want %q", path, got, want)
		}
	}
}

func TestHome(t *testing.T) {
	t.Setenv("HOME", "/home/me")

	if got := Path("~/.config/").ExpandHome(); got != "/home/me/.config/" {
		t.Errorf("ExpandHome() = %q", got)
	}
	if got := Path("/home/me/.cache").TransHome(); got != "$HOME/.cache" {
		t.Errorf("TransHome() = %q", got)
	}
}

func TestFilter(t *testing.T) {
	filter := NewFilter(nil, []string{"**/*.swp", "**/.DS_Store"})

	cases := map[Path]bool{
		"/vault/vim/default/vimrc":      true,
		"/vault/vim/default/.vimrc.swp": false,
		"/vault/vim/.DS_Store":          false,
		"/vault/vim/DS_Store":           true,
		"/vault/a.swp/vimrc":            true,
	}
	for path, want := range cases {
		if got := filter.Test(path); got != want {
			t.Errorf("Test(%q) = %v, want %v", path, got, want)
		}
	}
}
