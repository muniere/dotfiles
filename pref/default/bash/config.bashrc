if [ -f $SH_DOTDIR/config.shrc ]; then
  . $SH_DOTDIR/config.shrc
fi
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
for conf in `ls -d $BASH_DOTDIR/conf.d/*.*.bashrc`; do
  . $conf
done

# vim: ft=sh sw=2 ts=2 sts=2
