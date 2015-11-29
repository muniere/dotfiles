# dotfiles

## Get started

```bash
# clone
$ git clone https://github.com/muniere/dotfiles.git

# install 
$ ./xake install
```

## Tasks

Each task has following options:

- `-n`: dry-run
- `-v`: verbose 

### Dotfile

```bash
# install 
./xake install

# uninstall
./xake uninstall

# status
./xake status
```

### Homebrew

```bash
# install
./xake install brew

# uninstall
./xake uninstall brew

# status
./xake status bew
```

### Homebrew Cask

```bash
# install
./xake install cask

# uninstall
./xake uninstall cask

# status
./xake status cask
```

### Rubygems

```bash
# install
./xake install gem

# uninstall
./xake uninstall gem

# status
./xake status gem
```

### npm

```bash
# install
./xake install npm

# uninstall
./xake uninstall npm

# status
./xake status npm
```
