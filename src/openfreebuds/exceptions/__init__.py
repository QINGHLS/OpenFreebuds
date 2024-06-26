class FbError(Exception):
    pass


class FbNoDeviceError(FbError):
    pass


class FbPackageChecksumError(FbError):
    pass


class FbNotSupportedError(FbError):
    pass


class FbDriverError(FbError):
    pass


class FbNotReadyError(FbDriverError):
    pass


class FbMissingHandlerError(FbDriverError):
    pass


class FbStartupError(FbDriverError):
    pass
