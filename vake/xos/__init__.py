"""
Extend package of standard os package
"""

# 0th
from os import *

# 1st
import __builtin__ as builtin
import subprocess

#
# Constants
#
UBUNTU = "ubuntu"
DEBIAN = "debian"
CENTOS = "centos"
AMAZON = "amazon"
DARWIN = "darwin"

#
# Functions
#
def islinux():
    return sysname() in [UBUNTU, DEBIAN, CENTOS, AMAZON]


def isdarwin():
    return sysname() in [DARWIN]


def sysname():
    """
    Detect system name

    :return: Detected name
    """
    if xpath.isfile("/etc/issue"):
        rawname = builtin.open("/etc/issue").read().lower()
    else:
        rawname = subprocess.check_output(["uname", "-a"]).strip().lower()

    if "ubuntu" in rawname:
        return UBUNTU

    if "debian" in rawname:
        return DEBIAN

    if "centos" in rawname:
        return CENTOS

    if "amzn" in rawname:
        return AMAZON

    if "darwin" in rawname:
        return DARWIN

    return None


def listdir(pathname, recursive=False):
    """
    List entries in path

    :param pathname: Path
    :param recursive: Recursive or not
    :return: Entries in path
    """

    def isentry(dirpath, entname):
        return path.exists(path.join(dirpath, entname))

    return __list(pathname, cond=isentry, recursive=recursive)


def listdir_f(pathname, recursive=False):
    """
    List files in path

    :param pathname: Path
    :param recursive: Recursive or not
    :return: Files in path
    """

    def isfile(dirpath, entname):
        return path.isfile(path.join(dirpath, entname))

    return __list(pathname, cond=isfile, recursive=recursive)


def listdir_d(pathname, recursive=False):
    """
    List directories in path

    :param pathname: Path
    :param recursive: Recursive or not
    :return: Directories in path
    """

    def isdir(dirpath, entname):
        return path.isdir(path.join(dirpath, entname))

    return __list(pathname, cond=isdir, recursive=recursive)


def __list(pathname, cond, recursive=False):
    if not path.isdir(pathname):
        return [pathname]

    if not recursive:
        return listdir(pathname)

    entries = []

    for dirpath, dirnames, filenames in walk(pathname):
        entries.extend(
            map(lambda entname: path.join(dirpath, entname),
                filter(lambda entname: cond(dirpath, entname), dirnames + filenames)))

    return entries

# children
import xpath
