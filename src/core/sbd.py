from core.enums import Feedback


def format_sbd(tinh, cum, so):
    return f"{tinh:02d}{cum:02d}{so:04d}"


def sbd_generator(start_tinh, end_tinh):
    for tinh in range(start_tinh, end_tinh + 1):
        skip_tinh = False
        for cum in range(20):
            for so in range(10000):
                feedback = yield format_sbd(tinh, cum, so)
                if feedback is Feedback.STOP:
                    return
                elif feedback is Feedback.SKIP:
                    skip_tinh = True
                    break
            if skip_tinh:
                break
