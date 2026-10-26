package plist

import (
	"encoding/xml"
	"fmt"
	"io"
	"strconv"
	"strings"

	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/shell"
)

// Value is one of bool, float64, string, []Value and *Dict.
// Both <integer> and <real> are read as float64.
type Value = any

type Entry struct {
	Key   string
	Value Value
}

// Dict keeps its entries in document order.
type Dict struct {
	Entries []Entry
}

func (d *Dict) Get(key string) Value {
	if d == nil {
		return nil
	}
	for _, entry := range d.Entries {
		if entry.Key == key {
			return entry.Value
		}
	}
	return nil
}

const plistBuddy = "/usr/libexec/PlistBuddy"

type List struct {
	Path fspath.Path
	Root string
}

// GetDict returns nil when there is no such entry.
func (p *List) GetDict(key string) (*Dict, error) {
	result, err := p.get(p.entry(key), "xml")
	if err != nil {
		return nil, err
	}
	if !result.Status.Success {
		return nil, nil
	}

	value, err := parse(result.Stdout)
	if err != nil {
		return nil, err
	}
	dict, ok := value.(*Dict)
	if !ok {
		return nil, fmt.Errorf("plist: not a dict: %s", p.entry(key))
	}
	return dict, nil
}

func (p *List) SetBoolean(key string, value bool, options shell.Options) (shell.Status, error) {
	return p.set(p.entry(key), "bool", strconv.FormatBool(value), options)
}

func (p *List) SetString(key string, value string, options shell.Options) (shell.Status, error) {
	return p.set(p.entry(key), "string", value, options)
}

func (p *List) SetReal(key string, value float64, options shell.Options) (shell.Status, error) {
	return p.set(p.entry(key), "real", FormatNumber(value), options)
}

// SetDict replaces the entry with a dict of scalar values.
func (p *List) SetDict(key string, value []Entry, options shell.Options) (shell.Status, error) {
	entry := p.entry(key)
	if _, err := p.delete(entry, options); err != nil {
		return shell.Status{}, err
	}

	path := p.Path.ToAbsolute().String()

	status, err := shell.Call(plistBuddy, []string{"-c", fmt.Sprintf(`Add "%s" dict`, entry), path}, options)
	if err != nil {
		return shell.Status{}, err
	}
	for _, child := range value {
		kind, text := "string", fmt.Sprint(child.Value)
		switch v := child.Value.(type) {
		case bool:
			kind = "bool"
		case int:
			kind = "integer"
		case float64:
			kind, text = "real", FormatNumber(v)
		}
		command := fmt.Sprintf(`Add "%s:%s" %s %s`, entry, child.Key, kind, text)
		status, err = shell.Call(plistBuddy, []string{"-c", command, path}, options)
		if err != nil {
			return shell.Status{}, err
		}
	}
	return status, nil
}

func (p *List) Remove(key string, options shell.Options) (shell.Status, error) {
	return p.delete(p.entry(key), options)
}

func (p *List) get(entry string, format string) (shell.Result, error) {
	args := []string{"-c", fmt.Sprintf(`Print "%s"`, entry)}
	if format == "xml" {
		args = append(args, "-x")
	}
	args = append(args, p.Path.ToAbsolute().String())
	return shell.Capture(plistBuddy, args, shell.CaptureOptions{})
}

func (p *List) set(entry string, kind string, value string, options shell.Options) (shell.Status, error) {
	result, err := p.get(entry, "raw")
	if err != nil {
		return shell.Status{}, err
	}

	command := fmt.Sprintf(`Add "%s" %s %s`, entry, kind, value)
	if result.Status.Success {
		command = fmt.Sprintf(`Set "%s" %s`, entry, value)
	}
	return shell.Call(plistBuddy, []string{"-c", command, p.Path.ToAbsolute().String()}, options)
}

func (p *List) delete(entry string, options shell.Options) (shell.Status, error) {
	result, err := p.get(entry, "raw")
	if err != nil {
		return shell.Status{}, err
	}
	if !result.Status.Success {
		return shell.Status{Success: true, Code: 0}, nil
	}

	command := fmt.Sprintf(`Delete "%s"`, entry)
	return shell.Call(plistBuddy, []string{"-c", command, p.Path.ToAbsolute().String()}, options)
}

func (p *List) entry(key string) string {
	parts := []string{}
	for _, part := range []string{p.Root, key} {
		if part != "" {
			parts = append(parts, part)
		}
	}
	return strings.Join(parts, ":")
}

// FormatNumber prints a number in the shortest form that reads back the same.
func FormatNumber(value float64) string {
	return strconv.FormatFloat(value, 'f', -1, 64)
}

func parse(source string) (Value, error) {
	decoder := xml.NewDecoder(strings.NewReader(sanitize(source)))
	for {
		token, err := decoder.Token()
		if err != nil {
			return nil, fmt.Errorf("plist: no value found: %w", err)
		}
		start, ok := token.(xml.StartElement)
		if !ok {
			continue
		}
		if start.Name.Local == "plist" {
			continue
		}
		return parseValue(decoder, start)
	}
}

func parseValue(decoder *xml.Decoder, start xml.StartElement) (Value, error) {
	switch start.Name.Local {
	case "dict":
		dict := &Dict{}
		key := ""
		for {
			token, err := decoder.Token()
			if err != nil {
				return nil, err
			}
			switch token := token.(type) {
			case xml.EndElement:
				return dict, nil
			case xml.StartElement:
				if token.Name.Local == "key" {
					key, err = parseText(decoder)
					if err != nil {
						return nil, err
					}
					continue
				}
				value, err := parseValue(decoder, token)
				if err != nil {
					return nil, err
				}
				dict.Entries = append(dict.Entries, Entry{Key: key, Value: value})
			}
		}

	case "array":
		array := []Value{}
		for {
			token, err := decoder.Token()
			if err != nil {
				return nil, err
			}
			switch token := token.(type) {
			case xml.EndElement:
				return array, nil
			case xml.StartElement:
				value, err := parseValue(decoder, token)
				if err != nil {
					return nil, err
				}
				array = append(array, value)
			}
		}

	case "true", "false":
		if err := decoder.Skip(); err != nil {
			return nil, err
		}
		return start.Name.Local == "true", nil

	case "integer", "real":
		text, err := parseText(decoder)
		if err != nil {
			return nil, err
		}
		return strconv.ParseFloat(strings.TrimSpace(text), 64)

	default:
		// string, date and data
		return parseText(decoder)
	}
}

func parseText(decoder *xml.Decoder) (string, error) {
	var text strings.Builder
	for {
		token, err := decoder.Token()
		if err == io.EOF {
			return "", io.ErrUnexpectedEOF
		}
		if err != nil {
			return "", err
		}
		switch token := token.(type) {
		case xml.CharData:
			text.Write(token)
		case xml.EndElement:
			return text.String(), nil
		}
	}
}

// sanitize replaces characters that XML 1.0 forbids with U+FFFD.
// PlistBuddy prints control characters as they are, e.g. "^T" for a Ctrl+T hotkey in iTerm 2.
func sanitize(source string) string {
	return strings.Map(func(r rune) rune {
		switch {
		case r == '\t', r == '\n', r == '\r':
			return r
		case r < 0x20, r == 0xFFFE, r == 0xFFFF:
			return '�'
		default:
			return r
		}
	}, source)
}
