import subprocess
import os


def main() -> None:
    package_dir = os.path.expanduser('~') + '\\'
    executable_dir = '.FreeForm-Minesweeper'
    subprocess.run([
        'rmdir', package_dir + executable_dir, '/s', '/q'
    ], shell=True, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    main()
