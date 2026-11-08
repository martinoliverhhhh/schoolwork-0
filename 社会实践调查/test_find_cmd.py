import subprocess
import time
import win32gui
import win32con
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
p = subprocess.Popen([r"C:\Users\12559\Desktop\stata182025.lnk"], shell=True)
time.sleep(4)

stata_hwnd = None
def enum_cb(hwnd, lparam):
    global stata_hwnd
    if user32.IsWindowVisible(hwnd):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        if 'Stata/MP 18.0' in buf.value:
            stata_hwnd = hwnd
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

print(f"Stata HWND: {stata_hwnd}")

# Use PowerShell UIAutomation to find '命令'
ps_cmd = f'''
Add-Type -AssemblyName UIAutomationClient
$root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]{stata_hwnd})
$all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($e in $all) {{
    $name = $e.Current.Name
    $type = $e.Current.ControlType.ProgrammaticName
    $handle = $e.Current.NativeWindowHandle
    if ($name -like "*命令*" -or $name -like "*Command*") {{
        Write-Output "$type | Name: '$name' | Handle: $handle"
    }}
}}
'''
res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
print("Search results:")
print(res.stdout)

subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
