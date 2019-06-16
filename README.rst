Tamefox
=======

Puts Firefox/Chromium (or any program you want) to sleep when it does not have focus.

:Requires: python-xlib, xsel
:Usage: ./tamefox.py

To use the systemd unit:
   1) copy tamefox.service to `$HOME/.local/share/systemd/user/tamefox.service` and adjust path to the tamefox script
   2) execute `systemctl --user enable tamefox.service` to activate the unit and run it on login
   3) execute `systemctl --user start tamefox.service` to start the unit manually

