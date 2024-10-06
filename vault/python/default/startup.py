import atexit
import os
import readline

cachedir = os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
histdir = os.path.join(cachedir, 'python')
histfile = os.path.join(histdir, 'history')

def __startup__():
    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

def __shutdown__():
    os.makedirs(histdir, exist_ok=True)
    readline.write_history_file(histfile)

__startup__()
atexit.register(__shutdown__)
