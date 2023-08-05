# Copyright © Simon Harris-Palmer 2023. All rights reserved.

"""Installation Manager for FreeForm Minesweeper.

This file is NOT meant to be executed as a Python script.
It will not work properly. Refer to the executable version instead.
"""
import shutil
import subprocess
import sys
import tkinter as tk
import tkinter.ttk as ttk
from base64 import b64decode
from pathlib import Path
from platform import system, version
from time import sleep
from tkinter.messagebox import showerror

# region
ICON = b'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IDxHSU1QOkFQST4yLjA8L0dJTVA6QVBJPgogIDxHSU1QOlBsYXRmb3JtPkxpbnV4PC9HSU1QOlBsYXRmb3JtPgogIDxHSU1QOlRpbWVTdGFtcD4xNjc4Mjk2ODU2MDAzMjcyPC9HSU1QOlRpbWVTdGFtcD4KICA8R0lNUDpWZXJzaW9uPjIuMTAuMTg8L0dJTVA6VmVyc2lvbj4KIDwvcmRmOkRlc2NyaXB0aW9uPgoKIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PScnCiAgeG1sbnM6ZGM9J2h0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvJz4KICA8ZGM6Rm9ybWF0PmltYWdlL3BuZzwvZGM6Rm9ybWF0PgogIDxkYzpjcmVhdG9yPgogICA8cmRmOlNlcT4KICAgIDxyZGY6bGk+U2ltb24gSGFycmlzLVBhbG1lcjwvcmRmOmxpPgogICA8L3JkZjpTZXE+CiAgPC9kYzpjcmVhdG9yPgogIDxkYzpyaWdodHM+CiAgIDxyZGY6QWx0PgogICAgPHJkZjpsaSB4bWw6bGFuZz0neC1kZWZhdWx0Jz5Db3B5cmlnaHQgwqkgU2ltb24gSGFycmlzLVBhbG1lciAyMDIzLiBBbGwgcmlnaHRzIHJlc2VydmVkLjwvcmRmOmxpPgogICA8L3JkZjpBbHQ+CiAgPC9kYzpyaWdodHM+CiA8L3JkZjpEZXNjcmlwdGlvbj4KCiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0nJwogIHhtbG5zOnRpZmY9J2h0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvJz4KICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogPC9yZGY6RGVzY3JpcHRpb24+CgogPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9JycKICB4bWxuczp4bXA9J2h0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8nPgogIDx4bXA6Q3JlYXRvclRvb2w+R0lNUCAyLjEwPC94bXA6Q3JlYXRvclRvb2w+CiA8L3JkZjpEZXNjcmlwdGlvbj4KCiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0nJwogIHhtbG5zOnN0RXZ0PSdodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMnCiAgeG1sbnM6eG1wTU09J2h0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8nPgogIDx4bXBNTTpEb2N1bWVudElEPmdpbXA6ZG9jaWQ6Z2ltcDplMGEwNTkxZS1mZTczLTQ2MDItOTFiMi04ZjJjNTE2OTkyYjk8L3htcE1NOkRvY3VtZW50SUQ+CiAgPHhtcE1NOkhpc3Rvcnk+CiAgIDxyZGY6U2VxPgogICAgPHJkZjpsaSByZGY6cGFyc2VUeXBlPSdSZXNvdXJjZSc+CiAgICAgPHN0RXZ0OmFjdGlvbj5zYXZlZDwvc3RFdnQ6YWN0aW9uPgogICAgIDxzdEV2dDpjaGFuZ2VkPi88L3N0RXZ0OmNoYW5nZWQ+CiAgICAgPHN0RXZ0Omluc3RhbmNlSUQ+eG1wLmlpZDo2OTExMzU0Yy01OWQ5LTQ4Y2YtYTNmNC1lNzUzYjNjNjMwMmU8L3N0RXZ0Omluc3RhbmNlSUQ+CiAgICAgPHN0RXZ0OnNvZnR3YXJlQWdlbnQ+R2ltcCAyLjEwIChMaW51eCk8L3N0RXZ0OnNvZnR3YXJlQWdlbnQ+CiAgICAgPHN0RXZ0OndoZW4+MjAyMS0wNS0xMFQyMDo1NToyMS0wNDowMDwvc3RFdnQ6d2hlbj4KICAgIDwvcmRmOmxpPgogICAgPHJkZjpsaSByZGY6cGFyc2VUeXBlPSdSZXNvdXJjZSc+CiAgICAgPHN0RXZ0OmFjdGlvbj5zYXZlZDwvc3RFdnQ6YWN0aW9uPgogICAgIDxzdEV2dDpjaGFuZ2VkPi88L3N0RXZ0OmNoYW5nZWQ+CiAgICAgPHN0RXZ0Omluc3RhbmNlSUQ+eG1wLmlpZDphOWNhMmNlNC03MjZlLTQ0NTUtOGEyMC0xNDFjNGI3YWE4ZDc8L3N0RXZ0Omluc3RhbmNlSUQ+CiAgICAgPHN0RXZ0OnNvZnR3YXJlQWdlbnQ+R2ltcCAyLjEwIChMaW51eCk8L3N0RXZ0OnNvZnR3YXJlQWdlbnQ+CiAgICAgPHN0RXZ0OndoZW4+MjAyMS0wNS0xMVQxMToxOTowNi0wNDowMDwvc3RFdnQ6d2hlbj4KICAgIDwvcmRmOmxpPgogICAgPHJkZjpsaSByZGY6cGFyc2VUeXBlPSdSZXNvdXJjZSc+CiAgICAgPHN0RXZ0OmFjdGlvbj5zYXZlZDwvc3RFdnQ6YWN0aW9uPgogICAgIDxzdEV2dDpjaGFuZ2VkPi88L3N0RXZ0OmNoYW5nZWQ+CiAgICAgPHN0RXZ0Omluc3RhbmNlSUQ+eG1wLmlpZDoyYTc5YmU5Yy1lMmI0LTQ0NzAtOTNhOC01NmU4NTBkMDgxOTk8L3N0RXZ0Omluc3RhbmNlSUQ+CiAgICAgPHN0RXZ0OnNvZnR3YXJlQWdlbnQ+R2ltcCAyLjEwIChMaW51eCk8L3N0RXZ0OnNvZnR3YXJlQWdlbnQ+CiAgICAgPHN0RXZ0OndoZW4+MjAyMS0wNS0xMVQyMjowNDowMi0wNDowMDwvc3RFdnQ6d2hlbj4KICAgIDwvcmRmOmxpPgogICAgPHJkZjpsaSByZGY6cGFyc2VUeXBlPSdSZXNvdXJjZSc+CiAgICAgPHN0RXZ0OmFjdGlvbj5zYXZlZDwvc3RFdnQ6YWN0aW9uPgogICAgIDxzdEV2dDpjaGFuZ2VkPi88L3N0RXZ0OmNoYW5nZWQ+CiAgICAgPHN0RXZ0Omluc3RhbmNlSUQ+eG1wLmlpZDoyMGIwNjlhNS03NTliLTRmODEtYjdkZS1kZThjN2IxYjU4OTU8L3N0RXZ0Omluc3RhbmNlSUQ+CiAgICAgPHN0RXZ0OnNvZnR3YXJlQWdlbnQ+R2ltcCAyLjEwIChMaW51eCk8L3N0RXZ0OnNvZnR3YXJlQWdlbnQ+CiAgICAgPHN0RXZ0OndoZW4+MjAyMS0wNS0xN1QxOToyMjozMi0wNDowMDwvc3RFdnQ6d2hlbj4KICAgIDwvcmRmOmxpPgogICAgPHJkZjpsaSByZGY6cGFyc2VUeXBlPSdSZXNvdXJjZSc+CiAgICAgPHN0RXZ0OmFjdGlvbj5zYXZlZDwvc3RFdnQ6YWN0aW9uPgogICAgIDxzdEV2dDpjaGFuZ2VkPi88L3N0RXZ0OmNoYW5nZWQ+CiAgICAgPHN0RXZ0Omluc3RhbmNlSUQ+eG1wLmlpZDpkZTMxY2ViYS0xMWI5LTQ2NGYtOWQwNC0yNmI4NGVhYTIzZGU8L3N0RXZ0Omluc3RhbmNlSUQ+CiAgICAgPHN0RXZ0OnNvZnR3YXJlQWdlbnQ+R2ltcCAyLjEwIChMaW51eCk8L3N0RXZ0OnNvZnR3YXJlQWdlbnQ+CiAgICAgPHN0RXZ0OndoZW4+MjAyMS0wNS0xN1QyMDowMTo1MS0wNDowMDwvc3RFdnQ6d2hlbj4KICAgIDwvcmRmOmxpPgogICAgPHJkZjpsaSByZGY6cGFyc2VUeXBlPSdSZXNvdXJjZSc+CiAgICAgPHN0RXZ0OmFjdGlvbj5zYXZlZDwvc3RFdnQ6YWN0aW9uPgogICAgIDxzdEV2dDpjaGFuZ2VkPi88L3N0RXZ0OmNoYW5nZWQ+CiAgICAgPHN0RXZ0Omluc3RhbmNlSUQ+eG1wLmlpZDo3Yzg4MGNjYi0wZjUxLTQ4ZjctYTNlZi1jYzM4YzRkMGYyNDc8L3N0RXZ0Omluc3RhbmNlSUQ+CiAgICAgPHN0RXZ0OnNvZnR3YXJlQWdlbnQ+R2ltcCAyLjEwIChMaW51eCk8L3N0RXZ0OnNvZnR3YXJlQWdlbnQ+CiAgICAgPHN0RXZ0OndoZW4+LTA1OjAwPC9zdEV2dDp3aGVuPgogICAgPC9yZGY6bGk+CiAgIDwvcmRmOlNlcT4KICA8L3htcE1NOkhpc3Rvcnk+CiAgPHhtcE1NOkluc3RhbmNlSUQ+eG1wLmlpZDpmOGI0ZTZmNi1kMTkyLTQ0NzktYjcyOC0yMjZkYmQyZjFkMGQ8L3htcE1NOkluc3RhbmNlSUQ+CiAgPHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD54bXAuZGlkOjhkNTNkNDlmLWIzMzAtNDVkOC1hNzY4LTRjMWU2MDY4YTBjNTwveG1wTU06T3JpZ2luYWxEb2N1bWVudElEPgogPC9yZGY6RGVzY3JpcHRpb24+CjwvcmRmOlJERj4KPC94OnhtcG1ldGE+Cjw/eHBhY2tldCBlbmQ9J3InPz4ZM1n6AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5wMIESIPb2hBUwAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAE/SURBVFjD7ZfNbsMgDMdtj1ZKzlz2NqmqPtU07cGmaeRpeumZXlDcE1VGIBjWsB1qKZcQ5f/zFxhkZoaGxsyAiDCOIwAAEDQ2RPwBo1oDGGMAEcEYA8z8txFAxGUEfG5SdjieVte/vz6zEZibOAVe2Dq9+l2vTiIQbyQVt05nxT2gdTobKTGAFy81KQRtIV4CQSXivbrcn2Xu42s5CNrC81gkhmGoL8JN94XwLCC1f6j3YZo+3t/+VwSeAE8AklZvTcU/DMA6DR2ei8SlrUyx8zxGf+VXkVcp8Q7P0SO6aCSzTmchUp7jyy76XqWmml7Fz4OaXbJXl+SAQmujVU3xlYhni/C3EDlxURfUQkjExW3oIaRdIBUv6gL/Qz/11o7li+6Yponnd7Vwbt98Kw7vaq1NhXe1OVDzCLQWBwC4Ac0PpclH+N0iAAAAAElFTkSuQmCC'
# endregion


class InstallationManager:
    """Install, update, and uninstall FreeForm Minesweeper."""

    def __init__(self, prepend: Path) -> None:
        """Initialize the Installation Manager.

        Args:
            prepend: The path the executable was called from.
        """
        self.alive = False
        self.game_files = prepend / Path('freeform_minesweeper')
        self.root = tk.Tk()
        self.root.iconphoto(False, tk.PhotoImage(data=b64decode(ICON)))
        self.root.iconname('Install FreeForm Minesweeper')
        self.root.title('Install FreeForm Minesweeper')
        self.root.resizable(False, False)
        self.root.wm_protocol('WM_DELETE_WINDOW', self.close)
        self.main_frame = ttk.Frame(self.root, padding=5)
        try:
            self.home_directory = Path.home()
        except RuntimeError:
            showerror(
                title='Installation Error',
                message=(
                    'Oops! It looks like a suitable home for the current '
                    'user could not be found. Make sure to run this installer '
                    'as a user, and that any related environment variables '
                    'are set properly.'
                ),
            )
            return

        self.operating_system = system()
        if self.operating_system == 'Linux':
            self.package_directory = self.home_directory / '.freeform_minesweeper'

        elif self.operating_system == 'Windows':
            windows_version = version().partition('.')[0]
            supported_windows_versions = ['8', '10', '11']
            if windows_version not in supported_windows_versions:
                showerror(
                    title='Installation Error',
                    message=('Oops! This version of Windows is not supported.'),
                )
            self.package_directory = (
                self.home_directory / 'AppData/Local/FreeFormMinesweeper'
            )

        elif self.operating_system == '':
            showerror(
                title='Installation Error',
                message=('Oops! The operating system could not be identified.'),
            )
            return
        else:
            showerror(
                title='Installation Error',
                message=('Oops! This operating system is not supported.'),
            )
            return

        self.init_ui()
        self.alive = True

    def init_ui(self) -> None:
        """Construct UI."""
        thanks_label = ttk.Label(
            self.main_frame,
            text='Thank you for downloading FreeForm Minesweeper!',
        )
        install_label = ttk.Label(self.main_frame)
        button_frame = ttk.Frame(self.main_frame)
        if self.package_directory.exists():
            install_label.config(
                text=(
                    'It seems you have FreeForm Minesweeper already installed.\n'
                    'Would you like to update, or uninstall FreeForm Minesweeper?'
                ),
            )

            update_button = ttk.Button(
                button_frame,
                text='Update',
                cursor='hand2',
            )

            def update_callback():
                update_button.state([tk.DISABLED])
                uninstall_button.state([tk.DISABLED])
                self.install()

            update_button.config(command=update_callback)
            update_button.grid(row=0, column=0)

            uninstall_button = ttk.Button(
                button_frame,
                text='Uninstall',
                cursor='hand2',
            )

            def uninstall_callback():
                update_button.state([tk.DISABLED])
                uninstall_button.state([tk.DISABLED])
                self.uninstall()

            uninstall_button.config(command=uninstall_callback)
            uninstall_button.grid(row=0, column=1)

        else:
            install_label.config(
                text='Press the button below to install FreeForm Minesweeper.'
            )
            install_button = ttk.Button(
                button_frame,
                text='Install',
                cursor='hand2',
            )

            def install_callback():
                install_button.state([tk.DISABLED])
                self.install()

            install_button.config(command=install_callback)
            install_button.grid(row=0, column=0)

        close_button = ttk.Button(
            button_frame,
            text='Close',
            command=self.close,
            cursor='hand2',
        )
        close_button.grid(row=0, column=2)

        self.main_frame.grid(row=0, column=0)
        thanks_label.grid(row=0, column=0)
        install_label.grid(row=1, column=0)
        button_frame.grid(row=2, column=0, pady=5)

    def close(self) -> None:
        """Close window."""
        self.alive = False
        self.root.destroy()

    def install(self) -> None:
        """Install FFMS."""
        shutil.copytree(
            src=self.game_files,
            dst=self.package_directory,
            dirs_exist_ok=True,
        )
        shutil.copy2(
            src=sys.argv[0],
            dst=self.package_directory,
        )
        if self.operating_system == 'Linux':
            desktop = (
                self.home_directory
                / '.local/share/applications/freeform_minesweeper.desktop'
            )
            desktop_lines = (
                '[Desktop Entry]\n',
                'Name=FreeForm Minesweeper\n',
                'StartupWMClass=FreeForm Minesweeper\n',
                'Comment=Play FreeForm Minesweeper\n',
                'GenericName=Game\n',
                f'Exec=sh -c "cd {self.package_directory} && {self.package_directory / "freeform_minesweeper.sh"}"\n',
                f'Icon={self.package_directory / "assets" / "ui" / "light" / "32x32" / "new.png"}\n',
                'Type=Application\n',
            )
            with open(desktop, 'w') as desktop_fp:
                desktop_fp.writelines(desktop_lines)
        elif self.operating_system == 'Windows':
            # region
            ico_data = b'AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAABMLAAATCwAAAAAAAAAAAADAwMD/wMDA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/7+/v//AwMD/gICA/39/f/+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID////////////AwMD/v7+//4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP/+/v7//////8DAwP/AwMD/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA///////////////////////AwMD/wMDA/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/wUDAf8FAwH/BQMB/wUDAf8FAwH/BQMB/wUDAf8FAwH/wMDA/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/BQMB/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/8DAwP/AwMD/wMDA/8DAwP8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/wMDA/8DAwP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////AwMD/wMDA/8DAwP/AwMD/BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/wMDA/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP/AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/8DAwP8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////AwMD/BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf8FAwH/BQMB/wUDAf8FAwH/BQMB/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8AAAD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/AAAA/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/gICA/4CAgP+AgID/gICA//////////////////////8FAwH/Gf/3/xn/9/8Z//f/Gf/3/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/Gf/3/xn/9/8Z//f/Gf/3/wUDAf+AgID/gICA/4CAgP+AgID//////////////////////wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/4CAgP+AgID/gICA/4CAgP//////////////////////BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/gICA/4CAgP+AgID/gICA//////////////////////8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf+AgID/gICA/4CAgP+AgID//////////////////////wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/4CAgP+AgID/gICA/4CAgP//////////////////////BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/gICA/4CAgP+AgID/gICA//////////////////////8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf+AgID/gICA/4CAgP+AgID//////////////////////8DAwP8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/BQMB/wUDAf8Z//f/Gf/3/xn/9/8Z//f/BQMB/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8AAAD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf8FAwH/BQMB/xn/9/8Z//f/Gf/3/xn/9/8FAwH/BQMB/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wAAAP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/BQMB/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/wUDAf8FAwH/BQMB/xn/9/8Z//f/Gf/3/xn/9/8FAwH/wMDA/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP/AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/8DAwP/AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf/AwMD/wMDA/8DAwP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////AwMD/wMDA/8DAwP/AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/wMDA/8DAwP/AwMD/wMDA/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/BQMB/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/8DAwP8FAwH/BQMB/wUDAf8FAwH/BQMB/wUDAf8FAwH/BQMB/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/8DAwP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////AwMD/wMDA/4CAgP+AgID//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////7+/v//AwMD/gICA/39/f//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////AwMD/v7+////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////+/v7//////8DAwP/AwMD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='
            # endregion
            desktop = self.home_directory / 'Desktop/FreeFormMinesweeper.lnk'
            with open(self.package_directory / 'ffms.ico', 'wb') as fp:
                fp.write(b64decode(ico_data))
            desktop_vbs_lines = (
                'set fs  = CreateObject("Scripting.FileSystemObject")\n',
                'set ws  = WScript.CreateObject("WScript.Shell")\n',
                f'set link = ws.CreateShortcut("{desktop}")\n',
                f'link.TargetPath = "{self.package_directory / "freeform_minesweeper.exe"}"\n',
                f'link.WorkingDirectory = "{self.package_directory}"\n',
                f'link.IconLocation = "{self.package_directory / "ffms.ico"}"\n',
                'link.Save\n',
            )
            vbs_file_name = self.package_directory / 'shortcut.vbs'
            with open(vbs_file_name, 'w') as fp:
                fp.writelines(desktop_vbs_lines)
            subprocess.call(
                f'cscript {vbs_file_name}',
                stdout=subprocess.DEVNULL,
                # This constant is only present on Windows, but this code is only ran on Windows
                creationflags=subprocess.DETACHED_PROCESS,  # type: ignore
            )

        self.done()

    def uninstall(self) -> None:
        """Uninstall FFMS."""
        shutil.rmtree(
            self.package_directory,
            ignore_errors=True,
        )
        if self.operating_system == 'Linux':
            Path(
                self.home_directory
                / '.local/share/applications/freeform_minesweeper.desktop'
            ).unlink(missing_ok=True)
        elif self.operating_system == 'Windows':
            Path(self.home_directory / 'Desktop/FreeFormMinesweeper.lnk').unlink(
                missing_ok=True
            )
        self.done()

    def done(self) -> None:
        """Finished screen."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        done_label = ttk.Label(
            self.main_frame,
            text='Finished! You can safely close this installer.',
        )
        close_button = ttk.Button(
            self.main_frame,
            text='Close',
            command=self.close,
            cursor='hand2',
        )
        done_label.grid(row=0, column=0)
        close_button.grid(row=1, column=0, pady=5)

    def mainloop(self) -> None:
        """Run the UI."""
        while self.alive:
            try:
                self.root.update_idletasks()
                self.root.update()
            except tk.TclError:
                return
            sleep(0.01)


if __name__ == '__main__':
    im = InstallationManager(Path(sys.argv[0]).parent)
    im.mainloop()
