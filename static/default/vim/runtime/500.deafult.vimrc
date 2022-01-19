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
" Explore
"""
let g:netrw_liststyle=1
let g:netrw_banner=0
let g:netrw_preview=1
let g:netrw_timefmt="%Y/%m/%d(%a) %H:%M:%S"
let g:netrw_list_hide= '.*\.swp$,\~$,\.orig$'

let g:_netrw_open=0

function! ToggleNetrw(focus)
  if ! g:_netrw_open
    let g:_netrw_open=1
    if a:focus
      silent Explore %:p:h
    else
      silent Explore 
    endif
    return
  endif

  let i = bufnr("$")

  while (i >= 1)
    if (getbufvar(i, "&filetype") == "netrw")
      silent exe "bwipeout " . i
    endif
    let i-=1
  endwhile

  let g:_netrw_open=0
endfunction

nnoremap <silent> <C-e><C-e> :call ToggleNetrw(0)<CR>
inoremap <silent> <C-e><C-e> <ESC>:call ToggleNetrw(0)<CR>
nnoremap <silent> <C-e><C-f> :call ToggleNetrw(1)<CR>
inoremap <silent> <C-e><C-f> <ESC>:call ToggleNetrw(1)<CR>


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
Plug 'vim-scripts/surround.vim'

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
Plug 'vim-scripts/sudo.vim'

" == Fuzzy Finder
Plug 'ctrlpvim/ctrlp.vim'

nnoremap <silent> <C-x><C-f> :CtrlP .<CR>
inoremap <silent> <C-x><C-f> <ESC>:CtrlP .<CR>
nnoremap <silent> <C-x><C-b> :CtrlPBuffer<CR>
inoremap <silent> <C-x><C-b> <ESC>:CtrlPBuffer<CR>

if executable('ag')
  let g:ctrlp_use_caching=0
  let g:ctrlp_user_command='ag %s -i --nocolor --nogroup -g ""'
endif

call plug#end()

autocmd VimEnter * if len(filter(values(g:plugs), '!isdirectory(v:val.dir)'))
  \| PlugInstall --sync | source $MYVIMRC
\| endif

"""
" Appearance
"""
colorscheme muniere

" vim: ft=vim sw=2 ts=2 sts=2
