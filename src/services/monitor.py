from utils.stop import stop_event


def monitor_input():
    helper_text = """
HỆ THỐNG GIÁM SÁT LỆNH NGƯỜI DÙNG
---------------------------------
Y       : Dừng toàn bộ hệ thống
N       : Tiếp tục hệ thống
--help  : Hiển thị hướng dẫn này
---------------------------------
"""
    print("Monitor input đang chạy. Nhập '--help' để nhận trợ giúp.")

    while not stop_event.is_set():
        try:
            user_input = input("Nhập lệnh [Y/N]: ").strip().upper()

            if user_input == "Y":
                print("Lệnh dừng hệ thống được kích hoạt!")
                stop_event.set()
                break
            elif user_input == "N":
                print("Hệ thống tiếp tục hoạt động.")
            elif user_input == "--HELP":
                print(helper_text)
            else:
                print("Lệnh không hợp lệ. Nhập '--help' để được hướng dẫn.")

        except Exception:
            print("\nDừng hệ thống ngay lập tức.")
            stop_event.set()
            break
