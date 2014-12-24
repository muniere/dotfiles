setopt nonomatch

if [ -f $HOME/.sh.d/.shrc ]; then
  . $HOME/.sh.d/.shrc
fi
if [ -f /etc/zshrc ]; then
  . /etc/zshrc
fi
for conf in `ls -d $HOME/.zsh.d/*`; do
  . $conf
done

# vim:ft=zsh
