"""
Extend package of standard os.path package
"""

# 1st
import os
import re


def reduceuser(path):
    """
    Reduce user directory with '~'
    :param path: Path
    :return: Reduced path
    """

    if path[:1] == '~':
        return path

    if "HOME" in os.environ:
        return re.sub("^%s" % os.environ["HOME"], "~", path)
    else:
        return path
