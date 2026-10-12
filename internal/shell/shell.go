package shell

import (
	"bytes"
	"errors"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/logging"
)

type Status struct {
	Success bool
	Code    int
}

type Result struct {
	Status Status
	Stdout string
	Stderr string
}

// =====
// General
// =====
type Options struct {
	Cwd    string
	DryRun bool
	Logger *logging.Logger
}

// Call runs a command with the standard streams inherited.
// A non-zero exit is reported in the status, not as an error.
func Call(cmd string, args []string, options Options) (Status, error) {
	options.Logger.Tracef("%s", commandLine(options.Cwd, cmd, args))

	if options.DryRun {
		return Status{Success: true, Code: 0}, nil
	}

	command := exec.Command(cmd, args...)
	command.Dir = options.Cwd
	command.Stdin = os.Stdin
	command.Stdout = os.Stdout
	command.Stderr = os.Stderr

	return status(command.Run())
}

type CaptureOptions struct {
	Cwd    string
	Logger *logging.Logger
}

func Capture(cmd string, args []string, options CaptureOptions) (Result, error) {
	options.Logger.Tracef("%s", commandLine(options.Cwd, cmd, args))

	var stdout, stderr bytes.Buffer
	command := exec.Command(cmd, args...)
	command.Dir = options.Cwd
	command.Stdout = &stdout
	command.Stderr = &stderr

	status, err := status(command.Run())
	if err != nil {
		return Result{}, err
	}

	return Result{
		Status: status,
		Stdout: stdout.String(),
		Stderr: stderr.String(),
	}, nil
}

func commandLine(cwd string, cmd string, args []string) string {
	words := []string{}
	if cwd != "" {
		words = append(words, "cd", cwd, "&&")
	}
	words = append(words, cmd)
	words = append(words, args...)
	return strings.Join(words, " ")
}

func status(err error) (Status, error) {
	if err == nil {
		return Status{Success: true, Code: 0}, nil
	}
	var exit *exec.ExitError
	if errors.As(err, &exit) {
		return Status{Success: false, Code: exit.ExitCode()}, nil
	}
	return Status{}, err
}

// =====
// Short-hand
// =====
type MkdirOptions struct {
	Options
	Mode uint32
}

func Mkdir(path fspath.Path, options MkdirOptions) (Status, error) {
	args := []string{"-p"}
	if options.Mode != 0 {
		args = append(args, "-m", strconv.FormatUint(uint64(options.Mode), 8))
	}
	args = append(args, path.String())
	return Call("mkdir", args, options.Options)
}

func Symlink(src fspath.Path, dst fspath.Path, options Options) (Status, error) {
	return Call("ln", []string{"-s", "-f", src.String(), dst.String()}, options)
}

func Cp(src fspath.Path, dst fspath.Path, options Options) (Status, error) {
	return Call("cp", []string{src.String(), dst.String()}, options)
}

func Rm(path fspath.Path, options Options) (Status, error) {
	return Call("rm", []string{"-r", path.String()}, options)
}

func Chmod(path fspath.Path, mode string, options Options) (Status, error) {
	return Call("chmod", []string{mode, path.String()}, options)
}

func Touch(path fspath.Path, options Options) (Status, error) {
	return Call("touch", []string{path.String()}, options)
}

type CurlOptions struct {
	Options
	Output fspath.Path
}

func Curl(url string, options CurlOptions) (Status, error) {
	args := []string{"-f", "-S", "-L"}
	if options.Output != "" {
		args = append(args, "--create-dirs", "-o", options.Output.String())
	}
	args = append(args, url)
	return Call("curl", args, options.Options)
}
