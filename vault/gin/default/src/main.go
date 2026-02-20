package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func fail(message string) {
	fmt.Fprintln(os.Stderr, message)
	os.Exit(1)
}

func trimMargin(s string, margin string) string {
	lines := strings.Split(s, "\n")

	for len(lines) > 0 && strings.TrimSpace(lines[0]) == "" {
		lines = lines[1:]
	}
	for len(lines) > 0 && strings.TrimSpace(lines[len(lines)-1]) == "" {
		lines = lines[:len(lines)-1]
	}
	for i, line := range lines {
		if _, after, ok := strings.Cut(line, margin); ok {
			lines[i] = strings.TrimPrefix(after, " ")
		}
	}
	return strings.Join(lines, "\n")
}

type CaptureResult struct {
	success bool
	code    int
	stdout  string
	stderr  string
}

type CallResult struct {
	success bool
	code    int
}

type GitRef struct {
	name string
}

func (r GitRef) Short() string {
	if _, after, ok := strings.Cut(r.name, "refs/heads/"); ok {
		return after
	}

	return r.name
}

type GitWorktree struct {
	path string
	head string
	ref  GitRef
}

type Shell struct{}

var shell Shell

func (s Shell) call(command string, args []string) CallResult {
	cmd := exec.Command(command, args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	err := cmd.Run()
	if err == nil {
		return CallResult{success: true, code: 0}
	}

	if exitErr, ok := errors.AsType[*exec.ExitError](err); ok {
		return CallResult{
			success: false,
			code:    exitErr.ExitCode(),
		}
	}

	return CallResult{success: false, code: 1}
}

func (s Shell) capture(command string, args []string) CaptureResult {
	cmd := exec.Command(command, args...)
	out, err := cmd.CombinedOutput()
	text := strings.TrimRight(string(out), "\n")
	if err == nil {
		return CaptureResult{
			success: true,
			code:    0,
			stdout:  text,
			stderr:  "",
		}
	}

	if exitErr, ok := errors.AsType[*exec.ExitError](err); ok {
		return CaptureResult{
			success: false,
			code:    exitErr.ExitCode(),
			stdout:  "",
			stderr:  text,
		}
	}

	return CaptureResult{
		success: false,
		code:    1,
		stdout:  "",
		stderr:  text,
	}
}

type Helper struct{}

var helper Helper

func (h Helper) list() []GitWorktree {
	res := shell.capture("git", []string{"worktree", "list", "--porcelain"})
	if !res.success {
		if res.stderr != "" {
			fail(res.stderr)
		}
		fail("Error: failed to list worktrees")
	}

	lines := make([]string, 0)
	for line := range strings.SplitSeq(res.stdout, "\n") {
		if strings.TrimSpace(line) != "" {
			lines = append(lines, line)
		}
	}

	chunks := make([][]string, 0, len(lines)/3)
	for i := 0; i+2 < len(lines); i += 3 {
		chunks = append(chunks, lines[i:i+3])
	}

	rows := make([]GitWorktree, 0, len(chunks))
	for _, chunk := range chunks {
		path, ok := strings.CutPrefix(chunk[0], "worktree ")
		if !ok {
			continue
		}
		head, ok := strings.CutPrefix(chunk[1], "HEAD ")
		if !ok {
			continue
		}
		branch, ok := strings.CutPrefix(chunk[2], "branch ")
		if !ok {
			continue
		}

		rows = append(rows, GitWorktree{
			path: path,
			head: head,
			ref:  GitRef{name: branch},
		})
	}

	return rows
}

func (h Helper) discover(branch string) *string {
	entries := helper.list()
	for _, it := range entries {
		if it.ref.Short() == branch {
			return &it.path
		}
	}
	return nil
}

func (h Helper) prepare(branch string) string {
	res := shell.capture("git", []string{"rev-parse", "--show-toplevel"})
	if !res.success {
		if res.stderr != "" {
			fail(res.stderr)
		}
		fail("Error: not in a git repository")
	}

	repoRoot := res.stdout
	parent := filepath.Dir(repoRoot)
	repo := filepath.Base(repoRoot)
	normalized := strings.ReplaceAll(branch, "/", "-")
	return filepath.Join(parent, repo+"-"+normalized)
}

func (h Helper) add(args []string) CallResult {
	return shell.call("git", append([]string{"worktree", "add"}, args...))
}

func (h Helper) remove(path string) CallResult {
	return shell.call("git", []string{"worktree", "remove", path})
}

type CLI struct{}

var cli CLI

func (c CLI) help() {
	usage := `
		| Usage: gin <command> [options]
		|
		| Commands:
		|   list, ls                List all worktrees
		|   add <branch>            Create a worktree for an existing branch
		|   find <branch>           Resolve existing worktree path
		|   remove, rm <branch>     Remove a worktree
		|   help                    Show help
		|
		| Options:
		|   -h, --help              Show this help
	`
	fmt.Println(trimMargin(usage, "|"))
}

type listContext struct {
	porcelain bool
	help      bool
}

func (c CLI) list(args []string) {
	ctx, err := func(args []string) (*listContext, error) {
		fs := flag.NewFlagSet("list", flag.ContinueOnError)
		fs.SetOutput(io.Discard)
		porcelain := fs.Bool("porcelain", false, "machine readable output")
		help := fs.Bool("help", false, "show help")
		fs.BoolVar(help, "h", false, "show help")
		if err := fs.Parse(args); err != nil {
			return nil, err
		}

		return &listContext{
			porcelain: *porcelain,
			help:      *help,
		}, nil
	}(args)

	if err != nil {
		fail(err.Error())
	}

	if ctx.help {
		fmt.Println("Usage: gin list [--porcelain]")
		return
	}

	entries := helper.list()
	switch ctx.porcelain {
	case true:
		for _, it := range entries {
			fmt.Printf("worktree %s\n", it.path)
			fmt.Printf("HEAD %s\n", it.head)
			fmt.Printf("branch %s\n", it.ref.Short())
		}
	case false:
		pad := 0
		for _, it := range entries {
			if len(it.path) > pad {
				pad = len(it.path)
			}
		}
		for _, it := range entries {
			fmt.Printf("%-*s %s %s\n", pad, it.path, it.head, it.ref.Short())
		}
	}
}

type findContext struct {
	branch string
	help   bool
}

func (c CLI) find(args []string) {
	usage := `
		| Usage: gin find <branch>
		|
		| Options:
		|   -h, --help            Show this help
	`
	ctx, err := func(args []string) (*findContext, error) {
		fs := flag.NewFlagSet("find", flag.ContinueOnError)
		fs.SetOutput(io.Discard)
		help := fs.Bool("help", false, "show help")
		fs.BoolVar(help, "h", false, "show help")

		if err := fs.Parse(args); err != nil {
			return nil, err
		}

		if fs.NArg() == 0 {
			return nil, fmt.Errorf("Error: branch name required\n%s", trimMargin(usage, "|"))
		}
		if fs.NArg() > 1 {
			return nil, fmt.Errorf("Error: unexpected argument '%s'\n%s", fs.Arg(1), trimMargin(usage, "|"))
		}

		return &findContext{
			branch: fs.Arg(0),
			help:   *help,
		}, nil
	}(args)

	if err != nil {
		fail(err.Error())
	}

	if ctx.help {
		fmt.Println(trimMargin(usage, "|"))
		return
	}

	branch := ctx.branch
	path := helper.discover(branch)
	if path == nil {
		fail(fmt.Sprintf("Error: no worktree found for branch '%s'", branch))
	}

	fmt.Println(*path)
}

type addContext struct {
	branch string
	help   bool
}

func (c CLI) add(args []string) {
	usage := `
		| Usage: gin add <branch>
		|
		| Options:
		|   -h, --help            Show this help
	`
	ctx, err := func(args []string) (*addContext, error) {
		fs := flag.NewFlagSet("add", flag.ContinueOnError)
		fs.SetOutput(io.Discard)

		help := fs.Bool("help", false, "show help")
		fs.BoolVar(help, "h", false, "show help")

		if err := fs.Parse(args); err != nil {
			return nil, err
		}
		if *help {
			return &addContext{help: true}, nil
		}
		if fs.NArg() == 0 {
			return nil, fmt.Errorf("Error: branch name required\n%s", trimMargin(usage, "|"))
		}
		if fs.NArg() > 1 {
			return nil, fmt.Errorf("Error: unexpected argument '%s'\n%s", fs.Arg(1), trimMargin(usage, "|"))
		}

		return &addContext{
			branch: fs.Arg(0),
			help:   *help,
		}, nil
	}(args)

	if err != nil {
		fail(err.Error())
	}

	if ctx.help {
		fmt.Println(trimMargin(usage, "|"))
		return
	}

	branch := ctx.branch

	found := helper.discover(branch)
	if found != nil {
		fail(fmt.Sprintf("Error: worktree already exists for branch '%s' at '%s'", branch, *found))
	}

	target := helper.prepare(branch)
	status := helper.add([]string{target, branch})
	if !status.success {
		fail("Error: failed to create worktree")
	}
}

type removeContext struct {
	branches []string
	help     bool
}

func (c CLI) remove(args []string) {
	usage := `
		| Usage: gin remove <branch>
		|
		| Options:
		|   -h, --help            Show this help
	`
	ctx, err := func(args []string) (*removeContext, error) {
		fs := flag.NewFlagSet("remove", flag.ContinueOnError)
		fs.SetOutput(io.Discard)

		help := fs.Bool("help", false, "show help")
		fs.BoolVar(help, "h", false, "show help")

		if err := fs.Parse(args); err != nil {
			return nil, err
		}

		if fs.NArg() == 0 {
			return nil, fmt.Errorf("Error: branch name required\n%s", trimMargin(usage, "|"))
		}

		return &removeContext{
			branches: fs.Args(),
			help:     *help,
		}, nil
	}(args)

	if err != nil {
		fail(err.Error())
	}

	if ctx.help {
		fmt.Println(trimMargin(usage, "|"))
		return
	}

	for _, branch := range ctx.branches {
		path := helper.discover(branch)

		if path == nil {
			fail(fmt.Sprintf("Error: no worktree found for branch '%s'", branch))
		}

		status := helper.remove(*path)
		if !status.success {
			fail("Error: failed to remove worktree")
		}
	}
}

func main() {
	argv := os.Args[1:]
	if len(argv) == 0 {
		cli.help()
		fail("Error: command required")
	}

	if argv[0] == "-h" || argv[0] == "--help" {
		cli.help()
		return
	}

	command := argv[0]
	args := argv[1:]

	switch command {
	case "list", "ls":
		cli.list(args)
	case "find":
		cli.find(args)
	case "add":
		cli.add(args)
	case "remove", "rm":
		cli.remove(args)
	case "help":
		if len(args) > 0 {
			fail(fmt.Sprintf("Error: unexpected argument '%s'", args[0]))
		}
		cli.help()
	default:
		fail(fmt.Sprintf("Error: unknown command '%s'\nRun 'gin' without arguments for usage", command))
	}
}
