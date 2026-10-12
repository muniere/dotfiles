package idea

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

const sample = `<scheme name="Sample" version="142">
  <colors>
    <option name="CARET_COLOR" value="bbbbbb" />
  </colors>
  <attributes>
    <option name="PLAIN" value="1" />
    <option name="CONSOLE_RED_OUTPUT">
      <value>
        <option name="FOREGROUND" value="ff0000" />
        <option name="FONT_TYPE" value="2" />
      </value>
    </option>
    <option name="EMPTY">
      <value />
    </option>
    <option name="A&amp;B" baseAttributes="PLAIN" />
  </attributes>
</scheme>
`

func TestBuild(t *testing.T) {
	scheme, err := ParseColorScheme(sample)
	if err != nil {
		t.Fatal(err)
	}
	if got := scheme.Build(true); got != sample {
		t.Errorf("Build(true) =\n%s", got)
	}
	if got := scheme.Build(false); got != strings.TrimSuffix(sample, "\n") {
		t.Errorf("Build(false) =\n%s", got)
	}
}

func TestApply(t *testing.T) {
	scheme, err := ParseColorScheme(sample)
	if err != nil {
		t.Fatal(err)
	}
	scheme.ApplyDefaults(map[string]string{"PLAIN": "#00C7C7"})
	scheme.ApplyAttributes(map[string]string{"CONSOLE_RED_OUTPUT": "#000000", "EMPTY": "#ffffff"})

	want := strings.NewReplacer(
		`<option name="PLAIN" value="1" />`, `<option name="PLAIN" value="c7c7" />`,
		`<option name="FOREGROUND" value="ff0000" />`, `<option name="FOREGROUND" value="0" />`,
	).Replace(sample)
	if got := scheme.Build(true); got != want {
		t.Errorf("Build(true) =\n%s", got)
	}
}

// The color schemes in the vault must come out unchanged, or every link would rewrite them.
func TestBuildVault(t *testing.T) {
	paths, err := filepath.Glob("../../vault/*/darwin/colors/*.icls")
	if err != nil || len(paths) == 0 {
		t.Fatalf("no color schemes found: %v", err)
	}
	for _, path := range paths {
		content, err := os.ReadFile(path)
		if err != nil {
			t.Fatal(err)
		}
		source := string(content)

		scheme, err := ParseColorScheme(source)
		if err != nil {
			t.Fatalf("%s: %v", path, err)
		}
		if scheme.Build(strings.HasSuffix(source, "\n")) != source {
			t.Errorf("%s: not preserved", path)
		}
	}
}
