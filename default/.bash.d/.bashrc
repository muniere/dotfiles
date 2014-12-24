if [ -f $HOME/.sh.d/.shrc ]; then
  . $HOME/.sh.d/.shrc
fi
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
for conf in `ls -d $HOME/.bash.d/*`; do
  . $conf
done

# vim:ft=sh
