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
./xake link

# unlink
./xake unlink

# status
./xake list

# completion
./xake completion bash
./xake completion zsh
./xake completion fish
```
