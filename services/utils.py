import uuid
import sys
import subprocess
import os

def get_mac_address():
    """Returns the MAC address of the current machine."""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8*6, 8)][::-1])
    return mac

def hide_console():
    """Relaunches the script using pythonw.exe to hide the console window on Windows."""
    if sys.executable.endswith("python.exe"):
        # This is the visible python, relaunch with pythonw
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        if os.path.exists(pythonw):
            subprocess.Popen([pythonw] + sys.argv)
            sys.exit(0)
