import subprocess
import os


def main() -> None:
    package_dir = os.path.expanduser('~') + '/'
    binary_dir = 'FreeForm-Minesweeper/'
    hidden_marker = '.'
    binary_name = 'FreeForm-Minesweeper.sh'
    icon_dir_name = 'assets/icon_main.png'
    desktop_dir = '.local/share/applications/'
    desktop_name = 'freeform_minesweeper.desktop'
    desktop_lines = [
        '[Desktop Entry]\n',
        'Name=FreeForm Minesweeper\n',
        'StartupWMClass=FreeForm Minesweeper\n',
        'Comment=Play FreeForm Minesweeper\n',
        'GenericName=Game\n',
        f'Exec=sh -c "cd {package_dir + hidden_marker + binary_dir} && {package_dir + hidden_marker + binary_dir + binary_name}"\n',
        f'Icon={package_dir + hidden_marker + binary_dir + icon_dir_name}\n',
        'Type=Application\n'
    ]
    pwd = subprocess.run(['pwd'], capture_output=True, encoding='utf-8').stdout.strip() + '/'
    subprocess.run([
        'rm', '-r', package_dir + hidden_marker + binary_dir
    ], stderr=subprocess.DEVNULL)
    subprocess.run([
        'cp', '-r', pwd + binary_dir, package_dir + hidden_marker + binary_dir
    ])
    with open(package_dir + desktop_dir + desktop_name, 'w') as desktop_fp:
        desktop_fp.writelines(desktop_lines)


if __name__ == '__main__':
    main()
