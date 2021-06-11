import subprocess
import sys
import os
import winshell
from win32com.client import Dispatch


def main() -> None:
    package_dir = os.path.expanduser('~') + '\\'
    executable_dir = 'FreeForm-Minesweeper'
    executable_name = 'FreeForm-Minesweeper.exe'
    pwd = subprocess.run(
        ['cd'], capture_output=True, encoding=sys.getdefaultencoding(), shell=True
    ).stdout.strip() + '\\'
    subprocess.run([
        'rmdir', package_dir + executable_dir, '/s', '/q'
    ], shell=True, stderr=subprocess.DEVNULL)
    subprocess.run([
        'xcopy', pwd + executable_dir, package_dir + executable_dir, '/E', '/I'
    ], shell=True)

    desktop = winshell.desktop()
    path = os.path.join(desktop, "Freeform Minesweeper.lnk")
    target = package_dir + executable_dir + '\\' + executable_name
    w_dir = package_dir + executable_dir
    icon = package_dir + executable_dir + '\\assets\\icon_main.ico'
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = w_dir
    shortcut.IconLocation = icon
    shortcut.save()


if __name__ == '__main__':
    main()
