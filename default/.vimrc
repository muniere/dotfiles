for file in split(expand('$HOME/.vim.d/*'))
  exec 'source' file
endfor
