setopt nonomatch

if [ -f $SH_DOTDIR/rc.sh ]; then
  . $SH_DOTDIR/rc.sh
fi
if [ -f /etc/zshrc ]; then
  . /etc/zshrc
fi
for conf in `ls -d $ZSH_DOTDIR/rc.d/*.zsh`; do
  . $conf
done

# vim: ft=zsh sw=2 ts=2 sts=2
