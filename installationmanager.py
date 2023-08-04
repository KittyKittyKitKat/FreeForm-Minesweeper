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


class InstallationManager:
    """Install, update, and uninstall FreeForm Minesweeper."""

    def __init__(self, prepend: Path) -> None:
        """Initialize the Installation Manager.

        Args:
            prepend: The path the executable was called from.
        """
        self.alive = False
        self.game_files = prepend / Path('freeform_minesweeper')
        self.icon = 'assets/ui/light/32x32/new.png'

        self.root = tk.Tk()
        self.root.iconphoto(False, tk.PhotoImage(file=self.game_files / self.icon))
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
            src=self.game_files.parent,
            dst=self.package_directory,
            dirs_exist_ok=True,
        )
        if self.operating_system == 'Linux':
            desktop = (
                self.home_directory
                / '.local/share/applications/freeform_minesweeper.desktop'
            )
            binary_directory = self.package_directory / 'freeform_minesweeper'
            desktop_lines = (
                '[Desktop Entry]\n',
                'Name=FreeForm Minesweeper\n',
                'StartupWMClass=FreeForm Minesweeper\n',
                'Comment=Play FreeForm Minesweeper\n',
                'GenericName=Game\n',
                f'Exec=sh -c "cd {binary_directory} && {binary_directory / "freeform_minesweeper.sh"}"\n',
                f'Icon={binary_directory / self.icon}\n',
                'Type=Application\n',
            )
            with open(desktop, 'w') as desktop_fp:
                desktop_fp.writelines(desktop_lines)
        elif self.operating_system == 'Windows':
            # region
            ico_data = b'AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAABMLAAATCwAAAAAAAAAAAADAwMD/wMDA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/7+/v//AwMD/gICA/39/f/+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID////////////AwMD/v7+//4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP/+/v7//////8DAwP/AwMD/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA/4CAgP+AgID/gICA///////////////////////AwMD/wMDA/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/wUDAf8FAwH/BQMB/wUDAf8FAwH/BQMB/wUDAf8FAwH/wMDA/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/BQMB/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/8DAwP/AwMD/wMDA/8DAwP8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/wMDA/8DAwP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////AwMD/wMDA/8DAwP/AwMD/BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/wMDA/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP/AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/8DAwP8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////AwMD/BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf8FAwH/BQMB/wUDAf8FAwH/BQMB/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8AAAD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/AAAA/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/gICA/4CAgP+AgID/gICA//////////////////////8FAwH/Gf/3/xn/9/8Z//f/Gf/3/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/Gf/3/xn/9/8Z//f/Gf/3/wUDAf+AgID/gICA/4CAgP+AgID//////////////////////wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/4CAgP+AgID/gICA/4CAgP//////////////////////BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/gICA/4CAgP+AgID/gICA//////////////////////8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf+AgID/gICA/4CAgP+AgID//////////////////////wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/4CAgP+AgID/gICA/4CAgP//////////////////////BQMB/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/gICA/4CAgP+AgID/gICA//////////////////////8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf+AgID/gICA/4CAgP+AgID//////////////////////8DAwP8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/BQMB/wUDAf8Z//f/Gf/3/xn/9/8Z//f/BQMB/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8AAAD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf8FAwH/BQMB/xn/9/8Z//f/Gf/3/xn/9/8FAwH/BQMB/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wAAAP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/BQMB/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/wUDAf8FAwH/BQMB/xn/9/8Z//f/Gf/3/xn/9/8FAwH/wMDA/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP/AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/BQMB/8DAwP/AwMD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/8DAwP/AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/wUDAf/AwMD/wMDA/8DAwP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////AwMD/wMDA/8DAwP/AwMD/wMDA/wUDAf8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/wMDA/8DAwP/AwMD/wMDA/8DAwP+AgID/gICA/4CAgP+AgID//////////////////////8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/wUDAf8FAwH/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8Z//f/Gf/3/xn/9/8FAwH/BQMB/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/4CAgP+AgID/gICA/4CAgP//////////////////////wMDA/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/8DAwP8FAwH/BQMB/wUDAf8FAwH/BQMB/wUDAf8FAwH/BQMB/8DAwP/AwMD/wMDA/8DAwP/AwMD/wMDA/8DAwP/AwMD/gICA/4CAgP+AgID/gICA///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////AwMD/wMDA/4CAgP+AgID//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////7+/v//AwMD/gICA/39/f//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////AwMD/v7+////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////+/v7//////8DAwP/AwMD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='
            # endregion
            desktop = self.home_directory / 'Desktop/FreeFormMinesweeper.lnk'
            binary_directory = self.package_directory / 'freeform_minesweeper'
            with open(binary_directory / 'ffms.ico', 'wb') as fp:
                fp.write(b64decode(ico_data))
            desktop_vbs_lines = (
                'set fs  = CreateObject("Scripting.FileSystemObject")\n',
                'set ws  = WScript.CreateObject("WScript.Shell")\n',
                f'set link = ws.CreateShortcut("{desktop}")\n',
                f'link.TargetPath = "{binary_directory / "freeform_minesweeper.exe"}"\n',
                f'link.WorkingDirectory = "{binary_directory}"\n',
                f'link.IconLocation = "{binary_directory / "ffms.ico"}"\n',
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
