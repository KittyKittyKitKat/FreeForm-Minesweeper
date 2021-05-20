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
    binary_name = 'FreeForm-Minesweeper.sh'
    icon_dir_name = 'assets/icon_main.png'
    desktop_dir = '.local/share/applications/'
    desktop_name = 'freeform_minesweeper.desktop'
    script_name = 'ffmnswpr.sh'
    desktop_lines = [
        '[Desktop Entry]\n',
        'Name=FreeForm Minesweeper\n',
        'StartupWMClass=FreeForm Minesweeper\n',
        'Comment=Play FreeForm Minesweeper\n',
        'GenericName=Game\n',
        f'Exec=sh -c "cd {package_dir + binary_dir} && {package_dir + binary_dir + binary_name}"\n',
        f'Icon={package_dir + binary_dir + icon_dir_name}\n',
        'Type=Application\n'
    ]
    pwd = subprocess.run(['pwd'], capture_output=True, encoding='utf-8').stdout.strip() + '/'
    subprocess.run([
        'cp', '-R', pwd + binary_dir, package_dir
    ])
    with open(user_home + desktop_dir + desktop_name, 'w') as desktop_fp:
        desktop_fp.writelines(desktop_lines)


if __name__ == '__main__':
    main()
