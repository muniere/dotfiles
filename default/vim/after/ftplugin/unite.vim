nnoremap <silent> <buffer> <expr> <C-l> unite#do_action('split')
inoremap <silent> <buffer> <expr> <C-l> unite#do_action('split')
nnoremap <silent> <buffer> <expr> <C-j> unite#do_action('vsplit')
inoremap <silent> <buffer> <expr> <C-j> unite#do_action('vsplit')
inoremap <silent> <buffer> <expr> <C-u> unite_delete_backward_path

" Change hilight color
highlight PmenuSel term=underline cterm=underline ctermfg=0 ctermbg=7 gui=underline guibg=LightGrey
