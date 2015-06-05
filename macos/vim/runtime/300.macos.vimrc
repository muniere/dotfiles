" Plugins {{{1

" Disable filetype plugin temporary for setting up vundle plugin
filetype indent plugin off

call neobundle#begin(expand('~/.vim/bundle/'))

" Ruby {{{2
NeoBundle 'ruby.vim'
" }}}

" Python {{{2
NeoBundle 'hynek/vim-python-pep8-indent'
" }}}

" Javascript {{{2
NeoBundle 'jelera/vim-javascript-syntax'
NeoBundle 'jiangmiao/simple-javascript-indenter'
NeoBundle 'kchmck/vim-coffee-script'
let g:SimpleJsIndenter_BriefMode=1

NeoBundle 'myhere/vim-nodejs-complete'
" }}}

" AppleScript {{{2
NeoBundle 'applescript.vim'
" }}}

" Scala {{{2
NeoBundle 'scala.vim'
" }}}

" Go {{{2
set runtimepath+=$GOROOT/misc/vim
exe "set runtimepath+=".globpath($GOPATH, "src/github.com/nsf/gocode/vim")
exe "set runtimepath+=".globpath($GOPATH, "src/github.com/golang/lint/misc/vim")
NeoBundle 'Blackrush/vim-gocode'
" }}}

" CQL {{{2
NeoBundle 'elubow/cql-vim'
" }}}

" HTML {{{2
NeoBundle 'mattn/emmet-vim'
NeoBundle 'othree/html5.vim'
"}}}

" Jade {{{2
NeoBundle 'digitaltoad/vim-jade'
" }}}

" Handlebars {{{2
NeoBundle 'nono/vim-handlebars'
" }}}

" YAML {{{2
NeoBundle 'vim-scripts/yaml.vim'
" }}}
call neobundle#end()

filetype indent plugin on

NeoBundleCheck
" }}}

autocmd Filetype * set formatoptions-=r
autocmd Filetype * set formatoptions-=o
