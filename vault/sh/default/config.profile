for conf in `ls -d $SH_DOTDIR/conf.d/*.profile`; do
  . $conf
done

# vim: ft=sh sw=2 ts=2 sts=2 
