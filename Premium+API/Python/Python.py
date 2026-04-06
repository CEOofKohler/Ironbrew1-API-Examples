import json
import requests


class IB1ApiError(Exception):
    def __init__(self, status_code: int, message: str, raw: str):
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.raw = raw


def read_error_message(response: requests.Response) -> str:
    content_type = (response.headers.get("Content-Type") or "").lower()
    text = response.text.strip()

    if "application/problem+json" in content_type or "application/json" in content_type:
        try:
            data = response.json()
            if isinstance(data, dict):
                return (
                    data.get("detail")
                    or data.get("error")
                    or data.get("title")
                    or text
                    or f"HTTP {response.status_code}"
                )
            if isinstance(data, str) and data.strip():
                return data.strip()
        except Exception:
            pass

    return text or f"HTTP {response.status_code}"


def ib1_error(response: requests.Response) -> None:
    if response.ok:
        return

    message = read_error_message(response)

    if response.status_code == 400:
        raise IB1ApiError(400, f"Invalid request: {message}", response.text)
    if response.status_code == 401:
        raise IB1ApiError(401, f"Authentication failed: {message}", response.text)
    if response.status_code == 403:
        raise IB1ApiError(403, f"Access denied: {message}", response.text)
    if response.status_code == 408:
        raise IB1ApiError(408, "Obfuscation timed out after 15 minutes", response.text)
    if response.status_code == 429:
        raise IB1ApiError(429, f"Rate limit hit: {message}", response.text)
    if response.status_code >= 500:
        raise IB1ApiError(response.status_code, f"Server error: {message}", response.text)

    raise IB1ApiError(response.status_code, message, response.text)


def obfuscate(
    source: str,
    api_key: str,
    url: str = "https://ironbrew1.com",
    platform: str = "universal",
    aggressive_optimizations: int = 2,
    intense_vm_scrambling: bool = True,
    anti_tamper: bool = True,
    enable_vm_compression: bool = True,
) -> str:
    response = requests.post(
        f"{url}/obfuscate",
        params={
            "platform": platform,
            "aggressiveOptimizations": aggressive_optimizations,
            "intenseVmScrambling": str(intense_vm_scrambling).lower(),
            "antiTamper": str(anti_tamper).lower(),
            "enableVmCompression": str(enable_vm_compression).lower(),
        },
        data=source.encode("utf-8"),
        headers={
            "Key": api_key,
            "Content-Type": "text/plain; charset=utf-8",
        },
        timeout=910,
    )

    ib1_error(response)
    return response.text


if __name__ == "__main__":
    src = 'print("test")'
    api_key = "APIKEYHERE"

    try:
        obfuscated = obfuscate(src, api_key)
        print(obfuscated)
    except IB1ApiError as e:
        print(f"Request failed: {e.message}")
        print(e.raw)
    except requests.Timeout:
        print("Request failed: the HTTP request timed out before the API finished responding")
    except requests.RequestException as e:
        print(f"Request failed: network error: {e}")