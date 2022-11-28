# dotfiles

## Get started

```bash
# clone
$ git clone https://github.com/muniere/dotfiles.git

# link dotfiles and binfiles
$ make bootstrap
```

## Tasks

Each task has following options:

- `-n`: dry-run
- `-v`: verbose 

```bash
# link 
deno task link

# unlink
deno task unlink

# status
deno task list

# completion
deno task completion:bash
deno task completion:zsh
deno task completion:fish
```
