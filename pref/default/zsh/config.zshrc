setopt nonomatch

if [ -f $HOME/.config/sh/config.shrc ]; then
  . $HOME/.config/sh/config.shrc
fi
if [ -f /etc/zshrc ]; then
  . /etc/zshrc
fi
for conf in `ls -d $HOME/.config/zsh/*.*.zshrc`; do
  . $conf
done

# vim: ft=zsh sw=2 ts=2 sts=2
