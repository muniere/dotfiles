from logging import (
    getLogger,
    StreamHandler,
)

from .__level__ import (
    DEBUG,
    EXEC,
    INFO,
    WARN,
    ERROR,
)

from .__formatter__ import (
    LabelFormatter
)

def bootstrap():
    from . import __bootstrap__

    __bootstrap__.run()
