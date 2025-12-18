from utils import (
    MAX_CUM,
    MAX_SO,
    MAX_TINH,
    START_CUM,
    START_SO,
    START_TINH,
    Feedback,
    SBDLevel,
    format_sbd,
)


class SBDGenerator:
    def __init__(self):
        self.ma_so = START_SO
        self.ma_cum = START_CUM
        self.ma_tinh = START_TINH

        self.level = SBDLevel.LEVEL_SO

    def _up_level(self):
        if self.level is SBDLevel.LEVEL_SO:
            self.level = SBDLevel.LEVEL_CUM
        elif self.level is SBDLevel.LEVEL_CUM:
            self.level = SBDLevel.LEVEL_TINH
        else:
            raise StopIteration("Đã đạt giới hạn dãy số!")

    def _increment(self):
        self.ma_so += 1
        if self.ma_so > MAX_SO:
            self.ma_so = START_SO
            self.ma_cum += 1
            self._up_level()

        if self.ma_cum > MAX_CUM:
            self.ma_so = START_SO
            self.ma_cum = START_CUM
            self.ma_tinh += 1
            self._up_level()

        if self.ma_tinh > MAX_TINH:
            raise StopIteration("Đã đạt giới hạn dãy số!")

    def _increment_manually(self):
        self.ma_so = START_SO
        if self.level is SBDLevel.LEVEL_SO:
            self.ma_cum += 1
        elif self.level is SBDLevel.LEVEL_CUM:
            self.ma_cum = START_CUM
            self.ma_tinh += 1
        else:
            raise StopIteration("Đã đạt giới hạn dãy số!")

        self._up_level()

    def next_sbd(self):
        while True:
            feedback = yield format_sbd(self.ma_so, self.ma_cum, self.ma_tinh)

            if feedback is Feedback.STOP:
                return

            if feedback is Feedback.FORCE_INCREMENT:
                self._increment_manually()
            else:
                self.level = SBDLevel.LEVEL_SO
                self._increment()
