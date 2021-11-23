import os
import re
import glob

from typing import Callable, List, Union


def pilot(path) -> 'Pilot':
    """
    Create a new Pilot for pathname.
    Returns pathname as it is when it is Pilot.

    :type pathname: str or Pilot
    :rtype: Pilot
    """
    if isinstance(path, Pilot):
        return path
    else:
        return Pilot(path)


class Pilot:

    def __init__(self, value: Union[str, 'Pilot']):
        if isinstance(value, Pilot):
            self.__pathname = value.pathname()
        else:
            self.__pathname = value

    def __str__(self):
        return self.__pathname

    def pathname(self) -> str:
        """
        Retruns current value

        :rtype: string
        :return: Current path
        """
        return self.__pathname

    def expanduser(self) -> 'Pilot':
        """
        Retruns a new pathname with expanding '~' to absolute path to user directory

        :rtype: Pilot
        :return: New Pilot
        """
        return Pilot(os.path.expanduser(self.__pathname))

    def reduceuser(self) -> 'Pilot':
        """
        Returns a new pathname with reducing user directory with '~'

        :rtype: Pilot
        :return: New Pilot
        """
        if self.__pathname[:1] == '~':
            return self

        if "HOME" in os.environ:
            new = re.sub("^%s" % os.environ["HOME"], "~", self.__pathname)
            return Pilot(new)
        else:
            return self

    def abspath(self) -> 'Pilot':
        """
        Returns a new pathname with absolute path

        :rtype: Pilot
        :return: New Pilot
        """
        return Pilot(os.path.abspath(self.__pathname))

    def relpath(self, start: Union[str, 'Pilot'] = '.') -> 'Pilot':
        """
        Returns a new pathname with relative path from start

        :rtype: Pilot
        :return: New Pilot
        """
        if isinstance(start, Pilot):
            base = start.pathname()
        else:
            base = start

        return Pilot(os.path.relpath(self.__pathname, base))

    def prepend(self, component: Union[str, 'Pilot']) -> 'Pilot':
        """
        Returns a new pathname with prepending path component

        :rtype: Pilot
        :return: New Pilot
        """
        if isinstance(component, Pilot):
            base = component.pathname()
        else:
            base = component

        return Pilot(os.path.join(base, self.__pathname))

    def append(self, component: Union[str, 'Pilot']) -> 'Pilot':
        """
        Returns a new pathname with appending path component

        :rtype: Pilot
        :return: New Pilot
        """
        if isinstance(component, Pilot):
            base = component.pathname()
        else:
            base = component

        return Pilot(os.path.join(self.__pathname, base))

    def parent(self) -> 'Pilot':
        """
        Returns a new pathname of parent path

        :rtype: Pilot
        :return: New Pilot
        """
        return Pilot(os.path.dirname(self.__pathname))

    def exists(self) -> 'Pilot':
        """
        Returns if entry exists at path.

        :rtype: bool
        :return: True if exists, else False
        """
        return os.path.exists(self.__pathname)

    def isfile(self) -> bool:
        """
        Returns if file exists at path.

        :rtype: bool
        :return: True if exists, else False
        """
        return os.path.isfile(self.__pathname)

    def isdir(self) -> bool:
        """
        Returns if directory exists at path.

        :rtype: bool
        :return: True if exists, else False
        """
        return os.path.isdir(self.__pathname)

    def islink(self) -> bool:
        """
        Returns if link exists at path.

        :rtype: bool
        :return: True if exists, else False
        """
        return os.path.islink(self.__pathname)

    def read(self) -> str:
        """
        Read the content of file at path.

        :rtype: str
        :return: The content of file
        """
        with open(self.__pathname, 'r') as file:
            return file.read()

    def readlines(self) -> List[str]:
        """
        Read the lines of file at path.

        :rtype: list
        :return: The content of file
        """
        return self.read().splitlines()

    def write(self, string: str) -> int:
        """
        Write the content to the file at path.

        :rtype: str
        :return: The bytes written
        """
        with open(self.__pathname, 'w') as file:
            return file.write(string)

    def glob(self) -> List[str]:
        """
        Return a list of paths matching a pathname pattern.

        :rtype: list
        :return: The list of paths matching pattern
        """
        return glob.glob(self.__pathname)

    def children(self, target: str = None, recursive: bool = False) -> List['Pilot']:
        """
        List entries in path

        :param pathname: Path
        :param target: Target type string
        :param recursive: Recursive or not
        :return: Entries in path
        """
        if target in ['f', 'file']:
            return self.__children(lambda p: p.isfile(), recursive=recursive)

        if target in ['d', 'directory']:
            return self.__children(lambda p: p.isdir(), recursive=recursive)

        return self.__children(lambda p: p.exists(), recursive=recursive)

    def __children(self, cond: Callable[['Pilot'], bool], recursive: bool = False):
        if not os.path.isdir(self.__pathname):
            return [self]

        if not recursive:
            return [self.append(c) for c in os.listdir(self.__pathname)]

        entries = []

        for dirpath, dirnames, filenames in os.walk(self.__pathname):
            children = [Pilot(dirpath).append(e) for e in dirnames + filenames]
            entries.extend([p for p in children if cond(p)])

        return entries
