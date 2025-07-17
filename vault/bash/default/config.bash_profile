if [ -f $SH_DOTDIR/config.profile ]; then
  . $SH_DOTDIR/config.profile
fi
for conf in `ls -d $BASH_DOTDIR/conf.d/*.bash_profile`; do
  . $conf
done

# vim: ft=bash sw=2 ts=2 sts=2 
