"Core exceptions raised by the phoenix client"


class PhoenixError(Exception):
    pass

class PhoenixUnfoundError(PhoenixError):
    pass


class ConnectionError(PhoenixError):
    pass


class TimeoutError(PhoenixError):
    pass

class NotImplementedError(PhoenixError):
    pass


class PhoenixCommandExecuteError(PhoenixError):
    pass


class BusyLoadingError(ConnectionError):
    pass


class InvalidResponse(PhoenixError):
    pass


class ResponseError(PhoenixError):
    pass


class DataError(PhoenixError):
    pass

