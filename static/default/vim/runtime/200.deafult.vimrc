" Vim configurations for all environments
" Reference: http://vim.wikia.com/wiki/Example_vimc

"""
" Features
""

" Enable vim extended features
set nocompatible

" Default charset is utf-8
set encoding=utf8

" Use 256 true colors
set t_Co=256

" Enable show other buffers without saving current buffer
set hidden

" Enable commandline completion
set wildmenu

" Show command at the bottom
set showcmd

" Hilight search result
set hlsearch

" Backup
set backupskip=/tmp/*,/private/tmp/*

" Do not show preview window when completion
set completeopt-=preview

" Ignore whitespace diff
set diffopt+=iwhite

" Ignore capital case and small case when text search
set ignorecase
set smartcase

" Enable backspace key
set backspace=indent,eol,start

" Enable autoindent
set autoindent

" Do not move to start of line when move to other line
set nostartofline

" Show ruler at the bottom
set ruler

" Always show staus line
set laststatus=2

" Confirm save or not if buffer has changed
set confirm

" Use visual bell instead of beap
set visualbell

" Disable visual bell
set t_vb=

" Enable mouse 
set mouse=a

" Set command line height
set cmdheight=1

" Show line number
set number

" Set timeout length of keycode
set notimeout ttimeout ttimeoutlen=200

" Turn off IME when switch to insert mode
set iminsert=0
set imsearch=0

" Set fold method to marker
set foldmethod=marker

" Enable modeline
set modeline
set modelines=5

" Use 4 spaces in place of tab
set shiftwidth=4
set softtabstop=4
set tabstop=4
set expandtab

" Set new window directions
set splitbelow
set splitright

" Shell script with bash mode
let g:is_bash=1

" Move to last edit position
autocmd BufReadPost * if line("'\"") > 0 && line("'\"") <= line("$") | exe "normal g`\"" | endif

" Do not continue comment line
autocmd Filetype * set formatoptions-=r
autocmd Filetype * set formatoptions-=o

"""
" Keymaps
"""

" Deactivate highlight
nnoremap <C-l> :nohl<CR><C-l>

" Move in visual line
nnoremap k gk
nnoremap j gj
nnoremap <Up> gk
nnoremap <Down> gj

" Tab utilization
nnoremap tt :tabnew<CR>
nnoremap td :tabclose<CR>
nnoremap tl :tabnext<CR>
nnoremap tn :tabnext<CR>
nnoremap th :tabprevious<CR>
nnoremap tp :tabprevious<CR>
nnoremap tm :tabmove

"""
" Plugins
"""

call plug#begin()

" == Appearance
Plug 'itchyny/lightline.vim'

let g:lightline = { 
  \ 'active'  : { 'left': [['mode'], ['relativepath'], ['modified']] },
  \ 'inactive': { 'left': [['mode'], ['relativepath'], ['modified']] }
  \ }

" == Text Editing
Plug 'vim-scripts/Align'

Plug 'vim-scripts/surround.vim'

Plug 'scrooloose/nerdcommenter'

Plug 'editorconfig/editorconfig-vim'

" == Completion
Plug 'vim-scripts/AutoComplPop'

function! InsertTabWrapper()
    let col = col('.') - 1
    if !col || getline('.')[col - 1] !~ '\k'
        return "\<Tab>"
    else
        return "\<C-y>"
    endif
endfunction

inoremap <Tab> <C-r>=InsertTabWrapper()<CR>
inoremap <S-Tab> <C-n>

" == File System
Plug 'scrooloose/nerdtree'

Plug 'jistr/vim-nerdtree-tabs'
let g:nerdtree_tabs_open_on_gui_startup = 0
let g:nerdtree_tabs_open_on_console_startup = 0
nnoremap <C-e><C-e> :NERDTreeTabsToggle<CR>
inoremap <C-e><C-e> <ESC>:NERDTreeTabsToggle<CR>
nnoremap <C-e><C-f> :NERDTreeTabsOpen<CR><C-w>p:NERDTreeTabsFind<CR>
inoremap <C-e><C-f> <ESC>:NERDTreeTabsOpen<CR><C-w>p:NERDTreeTabsFind<CR>

Plug 'kien/ctrlp.vim'
nnoremap <C-x><C-f> :CtrlP .<CR>
inoremap <C-x><C-f> <ESC>:CtrlP .<CR>
nnoremap <C-x><C-b> :CtrlPBuffer<CR>
inoremap <C-x><C-b> <ESC>:CtrlPBuffer<CR>

if executable('ag')
  let g:ctrlp_use_caching=0
  let g:ctrlp_user_command='ag %s -i --nocolor --nogroup -g ""'
endif

Plug 'vim-scripts/sudo.vim'

" == Syntax Highlight
Plug 'scrooloose/syntastic'

let g:syntastic_mode_map = { 
      \ 'mode': 'active',
      \ 'active_filetypes': [],
      \ 'passive_filetypes': ['java'] 
      \ }
let g:syntastic_html_tidy_ignore_errors = [
      \'proprietary attribute "ng-',
      \'proprietary attribute "v-'
      \]

" == Languages / JSONC
Plug 'neoclide/jsonc.vim', { 'for': 'json' }

" == Languages / Shell Script
Plug 'vim-scripts/sh.vim', { 'for': 'sh' }

" == Languages / Ruby
Plug 'vim-scripts/ruby.vim', { 'for': 'ruby' }

" == Languages / Python
Plug 'hynek/vim-python-pep8-indent', { 'for': 'python' }

" == Languages / Javascript
Plug 'jelera/vim-javascript-syntax', { 'for': 'javascript' }
Plug 'jiangmiao/simple-javascript-indenter', { 'for': 'javascript' }
Plug 'kchmck/vim-coffee-script', { 'for': 'javascript' }
let g:SimpleJsIndenter_BriefMode=1

Plug 'myhere/vim-nodejs-complete', { 'for': 'javascript' }
Plug 'posva/vim-vue', { 'for': 'vue' }

" == Languages / Scala
Plug 'vim-scripts/scala.vim', { 'for': 'scala' }

" == Languages / Go
set runtimepath+=$GOROOT/misc/vim
exe "set runtimepath+=".globpath($GOPATH, "src/github.com/nsf/gocode/vim")
exe "set runtimepath+=".globpath($GOPATH, "src/github.com/golang/lint/misc/vim")
Plug 'Blackrush/vim-gocode', { 'for': 'go' }

" == Languages / HTML
Plug 'mattn/emmet-vim', { 'for': 'html' }
Plug 'othree/html5.vim', { 'for': 'html' }

" == Languages / Jade
Plug 'digitaltoad/vim-jade', { 'for': 'pug' }

" == Languages / Handlebars
Plug 'nono/vim-handlebars', { 'for': 'handlebars.html' }

" == Languages / YAML
Plug 'vim-scripts/yaml.vim', { 'for': 'yaml' }

" == Languages / Swift
Plug 'toyamarinyon/vim-swift', { 'for': 'swift' }
Plug 'keith/swift.vim', { 'for': 'swift' }
Plug 'cfdrake/vim-carthage', { 'for': 'carthage' }

" == Languages / Kotlin
Plug 'udalov/kotlin-vim', { 'for': 'kotlin' }

" == Languages / Crystal
Plug 'rhysd/vim-crystal', { 'for': 'crystal' }

" == Languages / Elixir
Plug 'elixir-lang/vim-elixir', { 'for': 'elixir' }
Plug 'mattreduce/vim-mix', { 'for': 'elixir' }

call plug#end()

autocmd VimEnter * if len(filter(values(g:plugs), '!isdirectory(v:val.dir)'))
  \| PlugInstall --sync | source $MYVIMRC
\| endif

"""
" Appearance
"""
colorscheme muniere

" vim: ft=vim sw=2 ts=2 sts=2
