if [ -f $SH_DOTDIR/rc.sh ]; then
  . $SH_DOTDIR/rc.sh
fi
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
for conf in `ls -d $BASH_DOTDIR/conf.d/*.bashrc`; do
  . $conf
done

# vim: ft=sh sw=2 ts=2 sts=2
