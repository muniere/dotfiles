" folding
setlocal foldmethod=expr
setlocal foldexpr=CalcPHPFoldLevel(v:lnum)
function! CalcPHPFoldLevel(lnum)
    let l:line0 = getline(a:lnum)
    let l:line3 = getline(a:lnum + 3)
    if l:line0 =~ 'function'
        " method start
        return '>1'
    elseif l:line3 =~ '\s*/\*\*\s*'
        " method end
        return 0
    elseif l:line0 == '}'
        " class end
        return 0    
    else
        " others
        return '='   
    endif
endfunction
