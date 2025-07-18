if [ -f $SH_DOTDIR/profile.sh ]; then
  . $SH_DOTDIR/profile.sh
fi
for conf in `ls -d $ZSH_DOTDIR/conf.d/*.zprofile`; do
  . $conf
done

# vim: ft=zsh sw=2 ts=2 sts=2 
