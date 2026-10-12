package docker

import (
	"github.com/muniere/dotfiles/internal/chef"
	"github.com/muniere/dotfiles/internal/fspath"
	"github.com/muniere/dotfiles/internal/layout"
	"github.com/muniere/dotfiles/internal/platform"
)

const resDir = fspath.Path("/Applications/Docker.app/Contents/Resources")

var DockerCookBook = &chef.CookBook{
	Name:      "DockerCookBook",
	Container: layout.Vault().Join("docker/"),
	Prefs: []*chef.PrefSpec{
		chef.Pref(chef.Bind{
			Src: resDir.Join("etc/docker.bash-completion"),
			Dst: layout.Home.Data().Join("bash/bash_completion.d/docker"),
		}),
		chef.Pref(chef.Bind{
			Src: resDir.Join("etc/docker-compose.bash-completion"),
			Dst: layout.Home.Data().Join("bash/bash_completion.d/docker-compose"),
		}),
		chef.Pref(chef.Bind{
			Src: resDir.Join("etc/docker.zsh-completion"),
			Dst: layout.Home.Data().Join("zsh/site-functions/_docker"),
		}),
		chef.Pref(chef.Bind{
			Src: resDir.Join("etc/docker-compose.zsh-completion"),
			Dst: layout.Home.Data().Join("zsh/site-functions/_docker-compose"),
		}),
	},
	Platforms: []platform.Platform{platform.Darwin},
}
