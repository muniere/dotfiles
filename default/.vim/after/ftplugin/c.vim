" folding
setlocal foldmethod=marker

" indent
setlocal shiftwidth=2
setlocal softtabstop=2
setlocal tabstop=2

" map
nnoremap <C-g> :Gtags 
nnoremap <C-i> :Gtags -f %<CR>
nnoremap <C-j> :GtagsCursor<CR>
nnoremap <C-n> :cn<CR>
nnoremap <C-p> :cp<CR>
