if [ -f $SH_DOTDIR/config.profile ]; then
  . $SH_DOTDIR/config.profile
fi
for conf in `ls -d $ZSH_DOTDIR/conf.d/*.zprofile`; do
  . $conf
done

# vim: ft=zsh sw=2 ts=2 sts=2 
