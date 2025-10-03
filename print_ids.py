import subprocess
import re
from typing import Optional, Dict
import hashlib

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
        "IDENTIFIER_1": get_motherboard_serial(),
        "IDENTIFIER_2": get_system_uuid()
    }

def hash_value(value: str) -> str:
    """Return hex-encoded SHA-256 of input string"""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    ids = get_identifiers()
    for k, v in ids.items():
        if v:
            print(f"{k}: {hash_value(v)}")
        else:
            print(f"{k}: Not found")

