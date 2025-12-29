from orchestrator.system import orchestrator_system

if __name__ == "__main__":
    start = int(input("Hãy nhập tỉnh bắt đầu: "))
    end = int(input("Hãy nhập tỉnh kết thúc: "))
    orchestrator_system(num_driver=4, start_tinh=start, end_tinh=end)
