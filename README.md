# dotfiles

## Get started

```bash
# clone
$ git clone https://github.com/muniere/dotfiles.git

# deploy dotfiles and binfiles
$ ./xake deploy

# install packages
$ ./xake install
```

## Tasks

Each task has following options:

- `-n`: dry-run
- `-v`: verbose 

### Dotfile & Binfile

```bash
# deploy 
./xake deploy

# undeploy
./xake undeploy

# status
./xake status
```

### Packages

```bash
# install
./xake install

# uninstall
./xake uninstall

# status
./xake status
```
