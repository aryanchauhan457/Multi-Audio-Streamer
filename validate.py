# validate.py
import hmac
import subprocess
import re
from typing import Optional, Dict
import hashlib


# Replace these with the SHA-256 hex digests of the authorized values
AUTHORIZED_MB_HASH = "b2eae435f102c5a3391ab3be66c8b4015190f2d3974037bf14ecf9369bf3daa8"
AUTHORIZED_UUID_HASH = "1cc599dfc741c17acec06ed68858c026b60c1f93f3fa8131975e61b075f14a28"

def _try_wmi():
    try:
        import wmi  # type: ignore
        return wmi.WMI()
    except ImportError:
        return None

def get_motherboard_serial() -> Optional[str]:
    """Returns motherboard serial number (Win32_BaseBoard.SerialNumber)"""
    c = _try_wmi()
    if c:
        try:
            for board in c.Win32_BaseBoard():
                sn = getattr(board, "SerialNumber", None)
                if sn:
                    return str(sn).strip()
        except Exception:
            pass
    # Fallback using WMIC
    return _wmic_get("baseboard", "SerialNumber")

def get_system_uuid() -> Optional[str]:
    """Returns system UUID (Win32_ComputerSystemProduct.UUID)"""
    c = _try_wmi()
    if c:
        try:
            for sys in c.Win32_ComputerSystemProduct():
                uuid = getattr(sys, "UUID", None)
                if uuid and not uuid.startswith("00000000"):
                    return str(uuid).strip()
        except Exception:
            pass
    # Fallback using WMIC
    return _wmic_get("computersystemproduct", "UUID")

def _wmic_get(classname: str, prop: str) -> Optional[str]:
    """Run WMIC and extract a property value"""
    try:
        output = subprocess.check_output(
            ["wmic", classname, "get", prop, "/value"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        match = re.search(rf"{prop}=(.+)", output)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None

def get_identifiers() -> Dict[str, Optional[str]]:
    return {
        "motherboard_serial": get_motherboard_serial(),
        "system_uuid": get_system_uuid()
    }

def hash_value(value: str) -> str:
    """Return hex-encoded SHA-256 of input string"""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_authorized(ids: dict) -> bool:
    mb = ids.get("motherboard_serial")
    uuid = ids.get("system_uuid")

    # If either value missing, it's unauthorized
    if not mb or not uuid:
        return False

    mb_hash = hash_value(mb)
    uuid_hash = hash_value(uuid)

    # Use constant-time comparison
    return (
        hmac.compare_digest(mb_hash, AUTHORIZED_MB_HASH) and
        hmac.compare_digest(uuid_hash, AUTHORIZED_UUID_HASH)
    )

if __name__ == "__main__":
    ids = get_identifiers()
    if is_authorized(ids):
        print("Access granted.")
    else:
        print("Unauthorized machine.")
