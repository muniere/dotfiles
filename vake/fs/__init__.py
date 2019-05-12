import os

def walk(top, topdown=True, onerror=None, followlinks=False):
  return os.walk(top, topdown, onerror, followlinks)

def children(pathname, target=None, recursive=False):
    """
    List entries in path

    :param pathname: Path
    :param recursive: Recursive or not
    :return: Entries in path
    """

    def isentry(dirpath, entname):
        return os.path.exists(os.path.join(dirpath, entname))

    def isfile(dirpath, entname):
        return os.path.isfile(os.path.join(dirpath, entname))

    def isdir(dirpath, entname):
        return os.path.isdir(os.path.join(dirpath, entname))

    if target == 'file' or target == 'f':
        return __children(pathname, cond=isfile, recursive=recursive)

    if target == 'directory' or target == 'dir' or target == 'd':
        return __children(pathname, cond=isdir, recursive=recursive)

    return __children(pathname, cond=isentry, recursive=recursive)


def __children(pathname, cond, recursive=False):
    if not os.path.isdir(pathname):
        return [pathname]

    if not recursive:
        return children(pathname)

    entries = []

    for dirpath, dirnames, filenames in os.walk(pathname):
        entries.extend(
            map(lambda entname: os.path.join(dirpath, entname),
                filter(lambda entname: cond(dirpath, entname), dirnames + filenames)))

    return entries
