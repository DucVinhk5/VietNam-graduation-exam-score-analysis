from core.enums import Feedback


def format_sbd(tinh, so):
    return f"{tinh:02d}{so:06d}"


def sbd_generator(start_tinh, end_tinh):
    for tinh in range(start_tinh, end_tinh + 1):
        for so in range(1, 1_000_000):
            feedback = yield format_sbd(tinh, so)
            if feedback is Feedback.STOP:
                return
            elif feedback is Feedback.SKIP:
                break