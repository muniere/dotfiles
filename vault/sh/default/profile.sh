# Barrel file for .profile

for conf in `ls -d $SH_DOTDIR/profile.d/*.sh`; do
  . $conf
done

# vim: ft=sh sw=2 ts=2 sts=2 
