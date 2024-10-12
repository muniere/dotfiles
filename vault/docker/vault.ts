import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { Path } from "@dotfiles/lib/path.ts";
import { CookBook, PrefSpec } from "@dotfiles/lib/schema.ts";

const DockerResDir = new Path("/Applications/Docker.app/Contents/Resources");

export const DockerCookBook = new CookBook({
  name: "DockerCookBook",
  container: ResLayout.vault().join("docker/"),
  prefs: [
    new PrefSpec({
      src: DockerResDir.join("etc/docker.bash-completion"),
      dst: HomeLayout.data().join("bash/bash_completion.d/docker"),
    }),
    new PrefSpec({
      src: DockerResDir.join("etc/docker-compose.bash-completion"),
      dst: HomeLayout.data().join("bash/bash_completion.d/docker-compose"),
    }),
    new PrefSpec({
      src: DockerResDir.join("etc/docker.zsh-completion"),
      dst: HomeLayout.data().join("zsh/site-functions/_docker"),
    }),
    new PrefSpec({
      src: DockerResDir.join("etc/docker-compose.zsh-completion"),
      dst: HomeLayout.data().join("zsh/site-functions/_docker-compose"),
    }),
  ],
  platforms: ["darwin"],
});
