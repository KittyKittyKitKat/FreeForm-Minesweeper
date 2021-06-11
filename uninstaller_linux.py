import subprocess
import os


def main() -> None:
    package_dir = os.path.expanduser('~') + '/'
    hidden_marker = '.'
    binary_dir = 'FreeForm-Minesweeper/'
    desktop_dir = '.local/share/applications/'
    desktop_name = 'freeform_minesweeper.desktop'
    subprocess.run([
        'rm', '-r', package_dir + hidden_marker + binary_dir
    ], stderr=subprocess.DEVNULL)
    subprocess.run([
        'rm', package_dir + desktop_dir + desktop_name
    ], stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    main()
