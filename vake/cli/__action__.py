class Action:

    INSTALL = "install"
    UNINSTALL = "uninstall"
    STATUS = "status"
    COMPLETION = "completion"

    @classmethod
    def values(cls):
        return [
            cls.INSTALL,
            cls.UNINSTALL,
            cls.STATUS,
            cls.COMPLETION,
        ]
