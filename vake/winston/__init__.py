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

from . import __bootstrap__

def bootstrap():
    __bootstrap__.run()
