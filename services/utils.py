import os
import winshell
from win32com.client import Dispatch

def set_startup(enabled=True):
    """Adds or removes the agent from Windows Startup."""
    startup_path = winshell.startup()
    shortcut_path = os.path.join(startup_path, "YouX_Agent.lnk")
    target_path = os.path.abspath("easyx.bat") # Path to our background runner
    
    if enabled:
        try:
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target_path
            shortcut.WorkingDirectory = os.path.abspath(".")
            shortcut.IconLocation = target_path
            shortcut.save()
            return True
        except Exception as e:
            print(f"[STARTUP ERROR] {e}")
            return False
    else:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
        return True

def get_composite_fingerprint():
    """
    Generates a unique hardware fingerprint using MAC, CPU ID, and Disk Serial.
    This makes it extremely hard to spoof or bypass activation.
    """
    try:
        # 1. Get MAC Address
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        
        # 2. Get CPU ID (Windows)
        cpu_id = subprocess.check_output("wmic cpu get processorid", shell=True).decode().split('\n')[1].strip()
        
        # 3. Get Disk Serial (C: Drive)
        disk_serial = subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split('\n')[1].strip()
        
        # Combine and Hash
        raw_id = f"{mac}-{cpu_id}-{disk_serial}"
        fingerprint = hashlib.sha256(raw_id.encode()).hexdigest()
        
        return {
            "mac": mac,
            "fingerprint": fingerprint,
            "raw_id": raw_id[:20] + "..." # For debugging
        }
    except Exception as e:
        # Fallback to simple MAC if WMIC fails (e.g. non-windows or restricted)
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        return {"mac": mac, "fingerprint": hashlib.md5(mac.encode()).hexdigest()}

def get_mac_address():
    # Keep for backward compatibility
    return ':'.join(re.findall('..', '%012x' % uuid.getnode()))
