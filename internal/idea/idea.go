package idea

import (
	"encoding/xml"
	"fmt"
	"io"
	"strings"
)

// ColorScheme represents a JetBrains IDE color scheme document.
//
// It parses, modifies and builds the color scheme files (.icls) used by
// JetBrains IDEs such as IntelliJ IDEA, Android Studio, PyCharm, etc.
type ColorScheme struct {
	root *node
}

type attribute struct {
	name  string
	value string
}

// node holds attributes and child elements only; a color scheme has no text.
type node struct {
	name     string
	attrs    []attribute
	children []*node
}

func (e *node) attr(name string) (string, bool) {
	for _, attr := range e.attrs {
		if attr.name == name {
			return attr.value, true
		}
	}
	return "", false
}

func (e *node) setAttr(name string, value string) {
	for i := range e.attrs {
		if e.attrs[i].name == name {
			e.attrs[i].value = value
			return
		}
	}
	e.attrs = append(e.attrs, attribute{name: name, value: value})
}

func (e *node) childrenOf(name string) []*node {
	children := []*node{}
	for _, child := range e.children {
		if child.name == name {
			children = append(children, child)
		}
	}
	return children
}

func ParseColorScheme(source string) (*ColorScheme, error) {
	decoder := xml.NewDecoder(strings.NewReader(source))

	var root *node
	stack := []*node{}
	for {
		token, err := decoder.Token()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, err
		}

		switch token := token.(type) {
		case xml.StartElement:
			element := &node{name: token.Name.Local}
			for _, attr := range token.Attr {
				element.attrs = append(element.attrs, attribute{name: attr.Name.Local, value: attr.Value})
			}
			if len(stack) > 0 {
				parent := stack[len(stack)-1]
				parent.children = append(parent.children, element)
			} else if root == nil {
				root = element
			}
			stack = append(stack, element)

		case xml.EndElement:
			stack = stack[:len(stack)-1]

		case xml.CharData:
			if strings.TrimSpace(string(token)) != "" {
				return nil, fmt.Errorf("idea: text content is not supported: %q", strings.TrimSpace(string(token)))
			}
		}
	}

	if root == nil {
		return nil, fmt.Errorf("idea: no root element")
	}
	return &ColorScheme{root: root}, nil
}

func formatColorHex(hex string) string {
	value := strings.TrimLeft(strings.ToLower(strings.Replace(hex, "#", "", 1)), "0")
	if value == "" {
		return "0"
	}
	return value
}

// options returns the `<option>` elements right under `<attributes>`.
func (d *ColorScheme) options() []*node {
	if d.root.name != "scheme" {
		return nil
	}
	options := []*node{}
	for _, attributes := range d.root.childrenOf("attributes") {
		options = append(options, attributes.childrenOf("option")...)
	}
	return options
}

// ApplyDefaults sets the `value` attribute of the options named in the palette.
//
//	<attributes>
//	  <option name="BLOCK_TERMINAL_DEFAULT_FOREGROUND" value="ffffff" />
//	</attributes>
func (d *ColorScheme) ApplyDefaults(palette map[string]string) {
	for _, option := range d.options() {
		name, _ := option.attr("name")
		color, ok := palette[name]
		if !ok {
			continue
		}
		option.setAttr("value", formatColorHex(color))
	}
}

// ApplyAttributes sets the `FOREGROUND` color of the options named in the palette.
//
//	<attributes>
//	  <option name="BLOCK_TERMINAL_BLACK">
//	    <value>
//	      <option name="FOREGROUND" value="000000" />
//	    </value>
//	  </option>
//	</attributes>
func (d *ColorScheme) ApplyAttributes(palette map[string]string) {
	for _, option := range d.options() {
		name, _ := option.attr("name")
		color, ok := palette[name]
		if !ok {
			continue
		}
		for _, value := range option.childrenOf("value") {
			for _, valueOption := range value.childrenOf("option") {
				if name, _ := valueOption.attr("name"); name == "FOREGROUND" {
					valueOption.setAttr("value", formatColorHex(color))
				}
			}
		}
	}
}

var escaper = strings.NewReplacer(
	"&", "&amp;",
	">", "&gt;",
	"<", "&lt;",
	"'", "&apos;",
	`"`, "&quot;",
)

func (d *ColorScheme) Build(trailingNewline bool) string {
	var b strings.Builder
	build(&b, d.root, 0)

	result := b.String()
	if !trailingNewline {
		return strings.TrimSuffix(result, "\n")
	}
	return result
}

func build(b *strings.Builder, element *node, depth int) {
	indent := strings.Repeat("  ", depth)

	b.WriteString(indent)
	b.WriteString("<")
	b.WriteString(element.name)
	for _, attr := range element.attrs {
		b.WriteString(" ")
		b.WriteString(attr.name)
		b.WriteString(`="`)
		b.WriteString(escaper.Replace(attr.value))
		b.WriteString(`"`)
	}

	if len(element.children) == 0 {
		b.WriteString(" />\n")
		return
	}

	b.WriteString(">\n")
	// siblings of the same name come together, in order of first appearance
	seen := map[string]bool{}
	for _, child := range element.children {
		if seen[child.name] {
			continue
		}
		seen[child.name] = true
		for _, sibling := range element.childrenOf(child.name) {
			build(b, sibling, depth+1)
		}
	}
	b.WriteString(indent)
	b.WriteString("</")
	b.WriteString(element.name)
	b.WriteString(">\n")
}
