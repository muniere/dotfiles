if [ -f $HOME/.config/sh/config.shrc ]; then
  . $HOME/.config/sh/config.shrc
fi
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
for conf in `ls -d $HOME/.config/bash/*.*.bashrc`; do
  . $conf
done

# vim: ft=sh sw=2 ts=2 sts=2