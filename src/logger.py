import threading
import time


# Mã màu ANSI
class Color:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


class Logger:
    LEVELS = {
        "DEBUG": {"priority": 10, "color": Color.CYAN},
        "INFO": {"priority": 20, "color": Color.GREEN},
        "WARNING": {"priority": 30, "color": Color.YELLOW},
        "ERROR": {"priority": 40, "color": Color.RED},
    }

    _lock = threading.Lock()  # thread-safe

    def __init__(self, filename="app.log", level="INFO", use_color=True):
        self.filename = filename
        self.level = level
        self.use_color = use_color

    def _log(self, level, msg):
        if Logger.LEVELS[level]["priority"] >= Logger.LEVELS[self.level]["priority"]:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            color = Logger.LEVELS[level]["color"] if self.use_color else ""
            reset = Color.RESET if self.use_color else ""
            log_line = f"{color}[{level}] {timestamp} | {msg}{reset}\n"
            with Logger._lock:
                with open(self.filename, "a", encoding="utf-8") as f:
                    f.write(log_line)

    def debug(self, msg):
        self._log("DEBUG", msg)

    def info(self, msg):
        self._log("INFO", msg)

    def warning(self, msg):
        self._log("WARNING", msg)

    def error(self, msg):
        self._log("ERROR", msg)


# Singleton
logger = Logger()
