import subprocess
import os
import sys


def main() -> None:
    try:
        user_home = f"/home/{os.environ['SUDO_USER']}/"
    except KeyError:
        sys.exit('Not executed as sudo')
    package_dir = '/usr/local/share/'
    binary_dir = 'FreeForm-Minesweeper/'
    desktop_dir = '.local/share/applications/'
    desktop_name = 'freeform_minesweeper.desktop'
    subprocess.run([
        'rm', '-r', package_dir + binary_dir
    ], stderr=subprocess.DEVNULL)
    subprocess.run([
        'rm', user_home + desktop_dir + desktop_name
    ], stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    main()
