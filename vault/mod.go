// Package vault lists the cook books, each of which lives next to the files of its tool.
package vault

import (
	"github.com/muniere/dotfiles/internal/chef"
	androidstudio "github.com/muniere/dotfiles/vault/AndroidStudio"
	code "github.com/muniere/dotfiles/vault/Code"
	intellijidea "github.com/muniere/dotfiles/vault/IntelliJIdea"
	xcode "github.com/muniere/dotfiles/vault/Xcode"
	"github.com/muniere/dotfiles/vault/asdf"
	"github.com/muniere/dotfiles/vault/bash"
	"github.com/muniere/dotfiles/vault/bat"
	"github.com/muniere/dotfiles/vault/claude"
	"github.com/muniere/dotfiles/vault/desktop"
	"github.com/muniere/dotfiles/vault/docker"
	"github.com/muniere/dotfiles/vault/gh"
	"github.com/muniere/dotfiles/vault/ghostty"
	"github.com/muniere/dotfiles/vault/git"
	"github.com/muniere/dotfiles/vault/gradle"
	"github.com/muniere/dotfiles/vault/herdr"
	"github.com/muniere/dotfiles/vault/hunk"
	"github.com/muniere/dotfiles/vault/iterm"
	"github.com/muniere/dotfiles/vault/launchd"
	"github.com/muniere/dotfiles/vault/mise"
	"github.com/muniere/dotfiles/vault/node"
	"github.com/muniere/dotfiles/vault/nvim"
	"github.com/muniere/dotfiles/vault/python"
	"github.com/muniere/dotfiles/vault/rio"
	"github.com/muniere/dotfiles/vault/sh"
	"github.com/muniere/dotfiles/vault/sqlfluff"
	terminalpalette "github.com/muniere/dotfiles/vault/terminal-palette"
	"github.com/muniere/dotfiles/vault/tig"
	"github.com/muniere/dotfiles/vault/tmux"
	"github.com/muniere/dotfiles/vault/vifm"
	"github.com/muniere/dotfiles/vault/vim"
	"github.com/muniere/dotfiles/vault/zsh"
	zshprompt "github.com/muniere/dotfiles/vault/zsh-prompt"
)

// Books lists the cook books in the order to link them.
func Books() []*chef.CookBook {
	return []*chef.CookBook{
		desktop.HomeCookBook,
		desktop.LibraryCookBook,
		sh.ShCookBook,
		bash.BashCookBook,
		zsh.ZshCookBook,
		zshprompt.ZshPromptCookBook,
		launchd.LaunchdCookBook,
		vim.VimCookBook,
		vifm.VifmCookBook,
		nvim.NeovimCookBook,
		bat.BatCookBook,
		git.GitCookBook,
		tig.TigCookBook,
		hunk.HunkCookBook,
		gh.GitHubCookBook,
		docker.DockerCookBook,
		asdf.AsdfCookBook,
		mise.MiseCookBook,
		mise.MiseCompletionCookBook,
		sqlfluff.SqlfluffCookBook,
		terminalpalette.TerminalPaletteCookBook,
		tmux.TmuxCookBook,
		herdr.HerdrCookBook,
		ghostty.GhosttyCookBook,
		rio.RioCookBook,
		gradle.GradleCookBook,
		python.PythonCookBook,
		node.NodeCookBook,
		claude.ClaudeCookBook,
		code.CodeCookBook,
		iterm.ITermCookBook,
		xcode.XcodeCookBook,
		intellijidea.IntelliJIdeaCookBook,
		androidstudio.AndroidStudioCookBook,
	}
}
