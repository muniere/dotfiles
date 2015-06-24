# dotfiles

## Requirements

- [Ruby](https://www.ruby-lang.org/) >= 1.8
- [Rake](http://docs.seattlerb.org/rake/) >= 0.8.0

## Get started

```bash
# install 
$ rake all:install

# uninstall
$ rake all:uninstall

# dry-run is supported
$ NOOP=true rake all:install
$ NOOP=true rake all:uninstall
```

## Show tasks

```bash
$ rake -T
rake all:install     # install all
rake all:uninstall   # uninstall all
rake brew:install    # install brew kegs
rake brew:uninstall  # uninstall brew kegs
rake dot:install     # install dotfiles
rake dot:status      # show dotfiles status
rake dot:uninstall   # uninstall dotfiles
rake gem:install     # install gems
rake gem:uninstall   # uninstall gems
rake jet:install     # install jetbrains preferences
rake jet:uninstall   # uninstall jetbrains preferences
rake npm:install     # install npm packages
rake npm:uninstall   # uninstall npm packages
```

