from . import __pilot__

def pilot(path):
    """
    Create a new Pilot for pathname.
    Returns pathname as it is when it is Pilot.

    :type pathname: str or Pilot
    :rtype: Pilot
    """
    if isinstance(path, __pilot__.Pilot):
        return path
    else:
        return __pilot__.Pilot(path)
