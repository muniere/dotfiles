setopt nonomatch

if [ -f $SH_DOTDIR/config.shrc ]; then
  . $SH_DOTDIR/config.shrc
fi
if [ -f /etc/zshrc ]; then
  . /etc/zshrc
fi
for conf in `ls -d $ZSH_DOTDIR/conf.d/*.zshrc`; do
  . $conf
done

# vim: ft=zsh sw=2 ts=2 sts=2
