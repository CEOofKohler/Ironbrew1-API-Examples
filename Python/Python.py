from pathlib import Path
import requests

BASE_URL = "https://ironbrew1.com"
EMAIL = "EMAILHERE"
PASSWORD = "PASSWORDHERE"

INPUT_PATH = "input.lua"
OUTPUT_PATH = "output.lua"

PLATFORM = "luau"
AGGRESSIVE_OPTIMIZATIONS = 2
INTENSE_VM_SCRAMBLING = True
ANTI_TAMPER = False
ENABLE_VM_COMPRESSION = False

source = Path(INPUT_PATH).read_text(encoding="utf-8")

session = requests.Session()

login_res = session.post(
    f"{BASE_URL}/login",
    json={
        "email": EMAIL,
        "password": PASSWORD,
        "rememberMe": True
    },
    timeout=30,
)
login_res.raise_for_status()

if "ib1_token" not in session.cookies:
    raise RuntimeError("Login succeeded but no ib1_token cookie was set")

params = {
    "platform": PLATFORM,
    "aggressiveOptimizations": AGGRESSIVE_OPTIMIZATIONS,
    "intenseVmScrambling": INTENSE_VM_SCRAMBLING,
    "antiTamper": ANTI_TAMPER,
    "enableVmCompression": ENABLE_VM_COMPRESSION,
}

obfuscate_res = session.post(
    f"{BASE_URL}/obfuscate",
    params=params,
    data=source.encode("utf-8"),
    headers={"Content-Type": "text/plain"},
    timeout=(30, 900),
)

obfuscate_res.raise_for_status()
Path(OUTPUT_PATH).write_bytes(obfuscate_res.content)
print(f"Saved obfuscated script to {OUTPUT_PATH}")