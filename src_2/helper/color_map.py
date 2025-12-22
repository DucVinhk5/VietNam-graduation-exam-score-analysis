# ---- Màu ANSI ----
GREEN = "\033[92m"  # Success
RED = "\033[91m"  # Fail
YELLOW = "\033[93m"  # Retry / Warning
RESET = "\033[0m"

# ---- Icon & màu map ----
STATUS_MAP = {"Success": ("[+]", GREEN), "Fail": ("[-]", RED), "Retry": ("[!]", YELLOW)}
