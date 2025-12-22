import asyncio
from orchestrator import orchestrate_scan


# Hàm main để chạy orchestrate_scan
def main():
    base_url = (
        "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-thi-tot-nghiep-thpt/2024"
    )
    asyncio.run(orchestrate_scan(base_url))


# Entry point
if __name__ == "__main__":
    main()
