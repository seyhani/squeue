from enum import IntEnum, Enum


def print_red(msg): print("\033[91m{}\033[00m".format(msg))


def print_green(msg): print("\033[92m{}\033[00m".format(msg))


def print_yellow(msg): print("\033[93m{}\033[00m".format(msg))


def print_cyan(msg): print("\033[96m{}\033[00m".format(msg))


def print_gray(msg): print("\033[97m{}\033[00m".format(msg))


class LogLevel(IntEnum):
    error = 1
    warn = 2
    info = 3
    debug = 4


color_log = {
    LogLevel.error: print_red,
    LogLevel.warn: print_yellow,
    LogLevel.info: print_cyan,
    LogLevel.debug: print_gray
}


class Logger:
    @staticmethod
    def log(level: LogLevel, msg: str):
        if Logger.level < level:
            return
        color_log.get(level, print)("[{}]: {}".format(level.name.ljust(5), msg))

    @staticmethod
    def error(msg: str):
        Logger.log(LogLevel.error, msg)

    @staticmethod
    def warn(msg: str):
        Logger.log(LogLevel.warn, msg)

    @staticmethod
    def info(msg: str):
        Logger.log(LogLevel.info, msg)

    @staticmethod
    def debug(msg: str):
        Logger.log(LogLevel.debug, msg)


Logger.level = LogLevel.error
