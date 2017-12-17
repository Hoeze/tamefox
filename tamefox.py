#!/usr/bin/python
# tamefox.py - Puts firefox & chromium to sleep when they do not have focus.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# (c) 2017 aexaey
#
# watch() function is (C) 2008-2013 Luke Macken <lmacken@redhat.com>, Jordan Sissel, Adam Jackson

from signal import SIGSTOP, SIGCONT
from Xlib import X, display, Xatom
from os import kill, system, stat, getuid
import re
import atexit

TAME = re.compile('.*Firefox|.*Chromium.*|.*Google Chrome.*')  # regex for windows that we wish to tame

# globals
waiting = set()
lastpid = False


def sig(pid, signal):
    if pid and pid > 1 and signal:
        if not getuid() or stat('/proc/%d' % pid).st_uid == getuid():
            kill(pid, signal)
        else:
            system("sudo -n kill -%d %d" % (signal, pid))


@atexit.register
def contall():
    for pid in waiting:
        sig(pid, SIGCONT)


def watch():
    """ A generator that yields events for a list of X properties """
    dpy = display.Display()
    screens = dpy.screen_count()
    atoms = {}
    wm_pid = dpy.get_atom('_NET_WM_PID')
    wm_client_leader = dpy.get_atom('WM_CLIENT_LEADER')

    for property in ['_NET_ACTIVE_WINDOW']:
        atomid = dpy.get_atom(property, only_if_exists=True)
        if atomid != X.NONE:
            atoms[atomid] = property

    for num in range(screens):
        screen = dpy.screen(num)
        screen.root.change_attributes(event_mask=X.PropertyChangeMask)

    while True:
        ev = dpy.next_event()
        if ev.type == X.PropertyNotify:
            if ev.atom in atoms:
                data = ev.window.get_full_property(ev.atom, 0)
                id = int(data.value.tolist()[0])
                window = dpy.create_resource_object('window', id)
                if window.id == 0:
                    continue
                parent = None
                try:
                    parent = window.get_full_property(wm_client_leader, 0)
                    parent = parent.value.tolist()[0]
                    parent = dpy.create_resource_object('window', parent)
                    parent = parent.get_full_property(Xatom.WM_NAME, 0).value
                except Exception, e:
                    print(str(e))
                try:
                    pid = window.get_full_property(wm_pid, 0)
                    pid = int(pid.value.tolist()[0])
                    title = window.get_full_property(Xatom.WM_NAME, 0).value
                except Exception, e:
                    print(str(e))
                    continue
                if title and pid:
                    yield title, pid


for title, pid in watch():
    if lastpid:
        system("xsel -k; xsel -bo | xsel -bi")
        waiting.add(lastpid)
        sig(lastpid, SIGSTOP)
        lastpid = False
    if TAME.match(title):
        sig(pid, SIGCONT)
        waiting.discard(pid)
        lastpid = pid
