" Vim configurations for all environments
" Reference: http://vim.wikia.com/wiki/Example_vimc

" Enable features {{{1

" Enable vim extended features
set nocompatible

" Enable filetyp plugin detecting filetype
filetype indent plugin on

" Enable syntax highlight
syntax on

" }}}

" Setup vim {{{1

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

" Set new window directions
set splitbelow
set splitright

" Move to last edit position
autocmd BufReadPost * if line("'\"") > 0 && line("'\"") <= line("$") | exe "normal g`\"" | endif

" Do not continue comment line
autocmd Filetype * set formatoptions-=r
autocmd Filetype * set formatoptions-=o

" Setup highlight color
highlight SpecialKey    ctermfg=4               term=bold
highlight NonText       ctermfg=12              term=bold
highlight Directory     ctermfg=4               term=bold
highlight ErrorMsg      ctermfg=15  ctermbg=1   term=standout
highlight IncSearch                             term=reverse            cterm=reverse
highlight Search                    ctermbg=11  term=reverse
highlight MoreMsg       ctermfg=2               term=bold 
highlight ModeMsg                               term=bold               cterm=bold
highlight LineNr        ctermfg=130             term=underline 
highlight CursorLineNr  ctermfg=130             term=bold 
highlight Question      ctermfg=2               term=standout 
highlight StatusLine                            term=bold,reverse       cterm=bold,reverse 
highlight StatusLineNC                          term=reverse            cterm=reverse 
highlight VertSplit                             term=reverse            cterm=reverse
highlight Title         ctermfg=5               term=bold 
highlight Visual                    ctermbg=7   term=reverse
highlight VisualNOS                             term=bold,underline     cterm=bold,underline
highlight WarningMsg    ctermfg=1               term=standout 
highlight WildMenu      ctermfg=0   ctermbg=11  term=standout 
highlight Folded        ctermfg=0   ctermbg=15  term=standout 
highlight FoldColumn    ctermfg=0   ctermbg=15  term=standout 
highlight DiffAdd       ctermfg=0   ctermbg=2   term=bold 
highlight DiffChange    ctermfg=0   ctermbg=3   term=bold 
highlight DiffDelete    ctermfg=0   ctermbg=6   term=bold 
highlight DiffText      ctermfg=0   ctermbg=7   term=reverse            cterm=bold 
highlight SignColumn    ctermfg=4   ctermbg=248 term=standout 
highlight Conceal       ctermfg=7   ctermbg=242 
highlight SpellBad                  ctermbg=224 term=reverse 
highlight SpellCap                  ctermbg=81  term=reverse 
highlight SpellRare                 ctermbg=225 term=reverse 
highlight SpellLocal                ctermbg=14  term=underline 
highlight Pmenu         ctermfg=0   ctermbg=225 
highlight PmenuSel      ctermfg=0   ctermbg=248 
highlight PmenuSbar                 ctermbg=248 
highlight PmenuThumb                ctermbg=0   
highlight TabLine       ctermfg=0   ctermbg=7   term=underline          cterm=underline 
highlight TabLineSel                            term=bold               cterm=bold 
highlight TabLineFill                           term=reverse            cterm=reverse 
highlight CursorColumn              ctermbg=7   term=reverse 
highlight CursorLine                            term=underline          cterm=underline 
highlight ColorColumn               ctermbg=224 term=reverse 
highlight MatchParen    ctermfg=0   ctermbg=7   term=reverse 
highlight Comment       ctermfg=4               term=bold 
highlight Constant      ctermfg=1               term=underline 
highlight Special       ctermfg=5               term=bold 
highlight Identifier    ctermfg=6               term=underline 
highlight Statement     ctermfg=130             term=bold 
highlight PreProc       ctermfg=5               term=underline 
highlight Type          ctermfg=2               term=underline 
highlight Underlined    ctermfg=5               term=underline          cterm=underline 
highlight Ignore        ctermfg=15              
highlight Error         ctermfg=15  ctermbg=9   term=reverse 
highlight Todo          ctermfg=0   ctermbg=11  term=standout 
highlight link Character      Constant
highlight link Number         Constant
highlight link Boolean        Constant
highlight link Float          Number
highlight link Function       Identifier
highlight link Conditional    Statement
highlight link Repeat         Statement
highlight link Label          Statement
highlight link Operator       Statement
highlight link Keyword        Statement
highlight link Exception      Statement
highlight link Include        PreProc
highlight link Define         PreProc
highlight link Macro          PreProc
highlight link PreCondit      PreProc
highlight link StorageClass   Type
highlight link Structure      Type
highlight link Typedef        Type
highlight link Tag            Special
highlight link SpecialChar    Special
highlight link Delimiter      Special
highlight link SpecialComment Special
highlight link Debug          Special
" }}}

" Indentation {{{1

" Use 4 spaces in place of tab
set shiftwidth=4
set softtabstop=4
set tabstop=4
set expandtab
" }}}

" Key mapping {{{1

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

" }}}

" Plugin {{{1

" Temporary disable filetype for vundle plugin
filetype off

" NeoBundle {{{2
if has('vim_starting')
    set runtimepath+=~/.vim/bundle/neobundle.vim
    call neobundle#begin(expand('~/.vim/bundle/'))
    NeoBundleFetch 'Shougo/neobundle.vim'
    call neobundle#end()
endif
" }}}

" ColorSchema {{{2

" Solarized {{{3
NeoBundle 'altercation/vim-colors-solarized'
" }}}

" Molokai {{{3
NeoBundle 'tomasr/molokai'
" }}}

" Wombat {{{3
NeoBundle 'vim-scripts/Wombat'
" }}}

" }}}

" NeoCompleCache {{{2
NeoBundle 'neocomplcache'

" Enable at startup
let g:neocomplcache_enable_at_startup = 1
let g:neocomplcache_lock_buffer_name_pattern = "files"
let g:neocomplcache_force_overwrite_completefunc = 1
" }}}

" NeoSnippet {{{2
NeoBundle 'Shougo/neosnippet'
NeoBundle 'Shougo/neosnippet-snippets'
let g:neosnippet#snippets_directory = '~/.vim/snippets'

" Autocomplete with tab key
imap <expr><TAB> neosnippet#expandable() <Bar><Bar> neosnippet#jumpable() ?  "\<Plug>(neosnippet_expand_or_jump)" : pumvisible() ? "\<C-n>" : "\<TAB>"
smap <expr><TAB> neosnippet#expandable() <Bar><Bar> neosnippet#jumpable() ?  "\<Plug>(neosnippet_expand_or_jump)" : "\<TAB>"
" }}}

" surround.vim {{{2
NeoBundle 'surround.vim'
"}}}

" NERD Commenter {{{2
NeoBundle 'scrooloose/nerdcommenter'
" }}}

" NERD Tree {{{2
NeoBundle 'scrooloose/nerdtree'
" }}}

" NERD Tree Tabs {{{2
NeoBundle 'jistr/vim-nerdtree-tabs'
let g:nerdtree_tabs_open_on_gui_startup = 0
let g:nerdtree_tabs_open_on_console_startup = 0
nnoremap <C-e><C-e> :NERDTreeTabsToggle<CR>
inoremap <C-e><C-e> <ESC>:NERDTreeTabsToggle<CR>
nnoremap <C-e><C-f> :NERDTreeTabsOpen<CR><C-w>p:NERDTreeTabsFind<CR>
inoremap <C-e><C-f> <ESC>:NERDTreeTabsOpen<CR><C-w>p:NERDTreeTabsFind<CR>
" }}}

" " Unite.vim {{{2
" NeoBundle 'Shougo/unite.vim'
" let g:unite_enable_start_insert = 1
" nnoremap <C-x><C-b> :Unite -buffer-name=files -direction=botright buffer<CR>
" nnoremap <C-x><C-f> :UniteWithBufferDir -buffer-name=files -direction=botright file<CR>
" nnoremap <C-x><C-r> :Unite -buffer-name=files -direction=botright file_mru<CR>
" " }}}

" ctlrp.vim {{{2
NeoBundle 'kien/ctrlp.vim'
nnoremap <C-x><C-f> :CtrlP .<CR>
inoremap <C-x><C-f> <ESC>:CtrlP .<CR>
nnoremap <C-x><C-b> :CtrlPBuffer<CR>
inoremap <C-x><C-b> <ESC>:CtrlPBuffer<CR>
" }}}

" Sudo.vim {{{2
NeoBundle 'sudo.vim'
" }}}

" BlockDiff {{{2
NeoBundle 'adie/BlockDiff'
" }}}

" gtags {{{2
NeoBundle 'gtags.vim'
" }}}

" Syntastic {{{2
NeoBundle 'scrooloose/syntastic'

let g:syntastic_mode_map = {
                            \'mode': 'active',
                            \ 'active_filetypes': [],
                            \ 'passive_filetypes': ['java']
                            \}
" }}}

" sh.vim {{{2
NeoBundle 'vim-scripts/sh.vim'
" }}}


" LightLine {{{2
NeoBundle 'itchyny/lightline.vim'

let g:lightline = {
            \   'active': {
            \       'left': [['mode'], ['relativepath'], ['modified']]
            \   },
            \   'inactive': {
            \       'left': [['mode'], ['relativepath'], ['modified']]
            \   }
            \ }
" }}}

" Align {{{2
NeoBundle 'Align'
" }}}

" YankRing {{{2
NeoBundle 'YankRing.vim'
let g:yankring_history_file = '.yankring_history'
" }}}

" fugitive {{{2
NeoBundle 'fugitive.vim'
" }}}

" JsonFormat {{{2
command! -nargs=0 JsonFormat :execute '%!python -m json.tool' 
" }}

" CdCurrent {{{2
command! -nargs=0 CdCurrent cd %:p:h
" }}}

let g:is_bash=1

" Enable filetype plugin
filetype indent plugin on

" }}}

" vim:ft=vim
