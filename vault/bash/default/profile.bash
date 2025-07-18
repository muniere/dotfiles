if [ -f $SH_DOTDIR/profile.sh ]; then
  . $SH_DOTDIR/profile.sh
fi
for conf in `ls -d $BASH_DOTDIR/profile.d/*.bash`; do
  . $conf
done

# vim: ft=bash sw=2 ts=2 sts=2 
