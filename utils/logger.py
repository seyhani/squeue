from enum import Enum


class LogLevel(Enum):
    error = 1
    warn = 2
    info = 3
    debug = 4


class Logger:
    @staticmethod
    def log(level: LogLevel, msg: str):
        if Logger.level >= level:
            print("[{}]:: {}".format(level, msg))

    @staticmethod
    def info(msg: str):
        Logger.log(LogLevel.info, msg)

    @staticmethod
    def warn(msg: str):
        Logger.log(LogLevel.warn, msg)


Logger.level = LogLevel.info
