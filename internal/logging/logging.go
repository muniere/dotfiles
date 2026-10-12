package logging

import (
	"fmt"
	"io"
	"os"

	"github.com/muniere/dotfiles/internal/ansi"
)

type Level struct {
	Value int
	Label string
}

var (
	LevelDebug = Level{Value: 10, Label: "DEBUG"}
	LevelTrace = Level{Value: 15, Label: "TRACE"}
	LevelMark  = Level{Value: 18, Label: "MARK"}
	LevelInfo  = Level{Value: 20, Label: "INFO"}
	LevelWarn  = Level{Value: 30, Label: "WARN"}
	LevelError = Level{Value: 40, Label: "ERROR"}
)

type Palette map[Level]ansi.Style

func DefaultPalette() Palette {
	return Palette{
		LevelDebug: ansi.Green,
		LevelTrace: ansi.Magenta,
		LevelMark:  ansi.White,
		LevelInfo:  ansi.Cyan,
		LevelWarn:  ansi.Yellow,
		LevelError: ansi.Red,
	}
}

func (p Palette) get(level Level) ansi.Style {
	if style, ok := p[level]; ok {
		return style
	}
	return ansi.Reset
}

type Options struct {
	Bold   bool
	NoTerm bool
}

// Logger accepts a nil receiver, so callers can log without checking for one.
type Logger struct {
	Level   Level
	Out     io.Writer
	Palette Palette
}

func New(level Level) *Logger {
	return &Logger{
		Level:   level,
		Out:     os.Stdout,
		Palette: DefaultPalette(),
	}
}

func (l *Logger) Log(message string, level Level, options ...Options) {
	if l == nil || level.Value < l.Level.Value {
		return
	}

	option := Options{}
	if len(options) > 0 {
		option = options[0]
	}

	decorate := l.Palette.get(level)
	if option.Bold {
		decorate = ansi.Styles(decorate, ansi.Bold)
	}

	terminator := "\n"
	if option.NoTerm {
		terminator = ""
	}

	plain := fmt.Sprintf("[%-5s] %s%s", level.Label, message, terminator)
	io.WriteString(l.Out, decorate(plain))
}

func (l *Logger) Debugf(format string, args ...any) {
	l.Log(fmt.Sprintf(format, args...), LevelDebug)
}

func (l *Logger) Tracef(format string, args ...any) {
	l.Log(fmt.Sprintf(format, args...), LevelTrace)
}

func (l *Logger) Markf(format string, args ...any) {
	l.Log(fmt.Sprintf(format, args...), LevelMark)
}

func (l *Logger) Infof(format string, args ...any) {
	l.Log(fmt.Sprintf(format, args...), LevelInfo)
}

func (l *Logger) Warnf(format string, args ...any) {
	l.Log(fmt.Sprintf(format, args...), LevelWarn)
}

func (l *Logger) Errorf(format string, args ...any) {
	l.Log(fmt.Sprintf(format, args...), LevelError)
}
