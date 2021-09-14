"""The game FreeForm Minesweeper, bundled with MultiMinesweeper mode.

Play the game by executing the file as a program, and have fun!
The only code intended to be executed is the main() function. Any other use may result in errors or other undefined behaviour.
"""
import base64
import random
import tkinter as tk
import time

from enum import Enum, auto
from itertools import chain, groupby
from os.path import expanduser
from platform import system as get_os
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font
from typing import Optional

import requests

from PIL import Image, ImageTk


class MetaData:
    """Provide variables and utitlies for checking current release against the most up to date release.

    Attributes:
        github_api_releases_url: URL to fetch data from.
        github_releases_url: URL to releases page for project.
        plaform: The OS of the system the program is running on.
        version: The version of the code, shipped with releases.

    """
    github_api_releases_url = 'https://api.github.com/repos/KittyKittyKitKat/FreeForm-Minesweeper/releases'
    github_releases_url = 'https://github.com/KittyKittyKitKat/FreeForm-Minesweeper/releases'
    platform = get_os()
    # This is a dummy variable for the purpose of source code.
    # The releases will have the proper information contained within
    # This information will directly correlate to the release info on GitHub
    version = 'vX.X.X'

    @staticmethod
    def get_release_tags(url: str) -> list[str]:
        """Fetch the releases tags from GitHub's repo API."""
        github_release_data = requests.get(url).json()
        tags = [release['tag_name'] for release in github_release_data]
        tags_linux, tags_windows = [
            list(g) for _, g in groupby(sorted(tags), key=lambda s: s[0])
        ]
        if MetaData.platform == 'Linux':
            return tags_linux
        elif MetaData.platform == 'Windows':
            return tags_windows

    @staticmethod
    def is_release_up_to_date() -> bool:
        """Compare release to most up to date."""
        if MetaData.version == 'vX.X.X':
            return True
        tags = MetaData.get_release_tags(MetaData.github_api_releases_url)
        if tags == '':
            messagebox.showwarning(
                title='OS Fetching Error',
                message=(
                    'Could not retrieve operating system information to queue updates.\n'
                    'You can safely ignore this message.'
                )
            )
            return True
        up_to_date_release = tags[-1]
        current_release = MetaData.platform + '-' + MetaData.version
        return up_to_date_release == current_release

    @staticmethod
    def outdated_notice() -> None:
        """Display pop up message detailing release is out of date."""
        message = (
            f'This release is not up to date, '
            'and as such you may be missing out on important new features or bug fixes.\n'
            f'Please go to {MetaData.github_releases_url} to download and install the lastest release.'
        )
        messagebox.showwarning(
            title='Outdated Release',
            message=message
        )


class ClickMode(Enum):
    """Enum represeting the current clicking mode of the game"""
    UNCOVER = auto()
    FLAG = auto()


class GameState(Enum):
    """Enum representing the current state of the game"""
    DONE = auto()
    PLAYING = auto()


class Difficulty(Enum):
    """Enum representing the difficulty values for the game, in percentages"""
    EASY = 0.13
    MEDIUM = 0.16
    HARD = 0.207
    EXPERT = 0.25


class Constants:
    """Container for various game constants.

    Attributes:
        BOARD_IMAGES: Sprites used for the base Minesweeper game.
        SEVSEG_IMAGES: Sprites used for seven segment displays.
        EXTENDED_BOARD_IMAGES: Sprites used for multimine mode.
        BOARD_SQUARE_SIZE: Size of a square on the board, in pixels.
        SEGMENT_HEIGHT: Height of a seven segment number, in pixels.
        SEGMENT_WIDTH: Width of a seven segment number, in pixels.
        PADDING_DIST: Padding distance to space various widgets, in pixels.
        BACKGROUND_COLOUR: Background colour of the window, in #rrggbb
        DEFAULT_COLOUR: Default colour of the window, in #rrggbb
        FONT: Smaller font used for in game text.
        FONT_BIG: Larger font used for in game text.
        MAINLOOP_TIME: Time spent sleeping in mainloop of game.
        LOCKED_BLACK_SQUARE: Sprite for a locked disabled square.
        UNLOCKED_BLACK_SQUARE: Sprint for an unlocked disabled square.
        FILE_EXTENSION: File extension used for saving and loading board files.
        FILE_TYPE: File type and extension, for file dialogues.
        LEADERBOARD_FILENAME: Path to the leaderboard JSON used to save times.
        SAVE_LOAD_DIR: Default directory for saving and loading board files.
        MAIN_ICON_ICO: Path to main window icon, relatively.
        SETTINGS_ICON_ICO: Path to settings window icon, relatively.
        LEADERBOARD_ICON_ICO: Path to leaderboard window icon, relatively.
    """
    BOARD_SQUARE_SIZE = 32
    SEGMENT_HEIGHT = 46
    SEGMENT_WIDTH = 26
    PADDING_DIST = 5
    BACKGROUND_COLOUR = '#c0c0c0'
    DEFAULT_COLOUR = '#d9d9d9'
    FONT = ('MINE-SWEEPER', 7, 'normal')
    FONT_BIG = ('MINE-SWEEPER', 9, 'normal')
    MAINLOOP_TIME = 0.01
    LOCKED_BLACK_SQUARE = Image.new('RGBA', size=(BOARD_SQUARE_SIZE, BOARD_SQUARE_SIZE), color=(0, 0, 0))
    UNLOCKED_BLACK_SQUARE = Image.new('RGBA', size=(BOARD_SQUARE_SIZE, BOARD_SQUARE_SIZE), color=(0, 0, 0))
    FILE_EXTENSION = '.ffmnswpr'
    FILE_TYPE = (('FreeForm Minesweeper Board', f'*{FILE_EXTENSION}'),)
    LEADERBOARD_FILENAME = 'assets/leaderboard.json'
    SAVE_LOAD_DIR = expanduser("~/Desktop")
    MAIN_ICON_ICO = 'assets/icon_main.ico'
    SETTINGS_ICON_ICO = 'assets/icon_settings.ico'

    @staticmethod
    def ternary(n):
        """Convert an integer to ternary"""
        if n == 0:
            return ''
        else:
            e = n // 3
            q = n % 3
            return Constants.ternary(e) + str(q)

    @staticmethod
    def init_board_images() -> None:
        """Initialize the images used for the game board

        First the proper sprite is drawn on UNLOCKED_BLACK_SQUARE
        Doing this procedurally keeps the spritesheet tidy
        The board spritesheet is load and cut into the individual squares
        All the PIL images are converted to PhotoImage objects for TKinter
        """
        ubs_x, ubs_y = Constants.UNLOCKED_BLACK_SQUARE.size
        for i in range(ubs_y):
            Constants.UNLOCKED_BLACK_SQUARE.putpixel((0, i), (128, 128, 128))
            Constants.UNLOCKED_BLACK_SQUARE.putpixel((1, i), (128, 128, 128))
        for i in range(ubs_x):
            Constants.UNLOCKED_BLACK_SQUARE.putpixel((i, 0), (128, 128, 128))
            Constants.UNLOCKED_BLACK_SQUARE.putpixel((i, 1), (128, 128, 128))
        Constants.UNLOCKED_BLACK_SQUARE = ImageTk.PhotoImage(image=Constants.UNLOCKED_BLACK_SQUARE)
        Constants.LOCKED_BLACK_SQUARE = ImageTk.PhotoImage(image=Constants.LOCKED_BLACK_SQUARE)
        BOARD_IMAGES = []
        with Image.open('assets/board_sheet.png') as board_sheet:
            x, y = board_sheet.size
            for i in range(0, y, Constants.BOARD_SQUARE_SIZE):
                for j in range(0, x, Constants.BOARD_SQUARE_SIZE):
                    im = board_sheet.crop((j, i, j + Constants.BOARD_SQUARE_SIZE, i + Constants.BOARD_SQUARE_SIZE))
                    im2 = ImageTk.PhotoImage(im)
                    BOARD_IMAGES.append(im2)
        setattr(Constants, 'BOARD_IMAGES', BOARD_IMAGES)

    @staticmethod
    def init_sevseg_images() -> None:
        """Initialize the images used for the seven segment displays

        The seven segment spritesheet is load and cut into the individual numbers
        All the PIL images are converted to PhotoImage objects for TKinter
        """
        SEVSEG_IMAGES = []
        with Image.open('assets/sevseg_sheet.png') as sevseg_sheet:
            x, y = sevseg_sheet.size
            for i in range(0, y, Constants.SEGMENT_HEIGHT):
                for j in range(0, x, Constants.SEGMENT_WIDTH):
                    im = sevseg_sheet.crop((j, i, j + Constants.SEGMENT_WIDTH, i + Constants.SEGMENT_HEIGHT))
                    im2 = ImageTk.PhotoImage(im)
                    SEVSEG_IMAGES.append(im2)
        setattr(Constants, 'SEVSEG_IMAGES', SEVSEG_IMAGES)

    @staticmethod
    def init_extended_board_images() -> None:
        """Initialize the images used for the multimine mode

        The extened board spritesheet is load and cut into the individual squares
        All the PIL images are converted to PhotoImage objects for TKinter
        """
        EXTENDED_BOARD_IMAGES = []
        with Image.open('assets/board_sheet_extended.png') as board_sheet:
            x, y = board_sheet.size
            for i in range(0, y, Constants.BOARD_SQUARE_SIZE):
                for j in range(0, x, Constants.BOARD_SQUARE_SIZE):
                    im = board_sheet.crop((j, i, j + Constants.BOARD_SQUARE_SIZE, i + Constants.BOARD_SQUARE_SIZE))
                    im2 = ImageTk.PhotoImage(im)
                    EXTENDED_BOARD_IMAGES.append(im2)
        setattr(Constants, 'EXTENDED_BOARD_IMAGES', EXTENDED_BOARD_IMAGES)

    @staticmethod
    def init_window_icons() -> None:
        """Initialize the images used for the window icons

        The PIL images are converted to PhotoImage objects for TKinter
        """
        MAIN_ICON = ImageTk.PhotoImage(Image.open('assets/icon_main.png'))
        SETTINGS_ICON = ImageTk.PhotoImage(Image.open('assets/icon_settings.png'))
        LEADERBOARD_ICON_PNG = ImageTk.PhotoImage(Image.open('assets/icon_leaderboard.png'))
        setattr(Constants, 'MAIN_ICON_PNG', MAIN_ICON)
        setattr(Constants, 'SETTINGS_ICON_PNG', SETTINGS_ICON)
        setattr(Constants, 'LEADERBOARD_ICON_PNG', LEADERBOARD_ICON_PNG)


class Options:
    """Container for utilites to customize the game

    Attributes:
        multimines: Flag if the game is in multimine mode.
        grace_rule: Flag if the grace rule is set.
        multimine_sq_inc: Probability of getting multimines buff.
        flagless: Flag if the game is in flagless mode.
        multimine_mine_inc: Percentage mine increase in multimine mode.
        rows: Number of rows in the game space.
        cols: DNumber of colummns in the game space.
        window_width: Width of the window, in pixels.
        board_height: Height of the game board, in pixels.

    """
    multimines = False
    grace_rule = True
    multimine_sq_inc = 0.1
    flagless = False
    multimine_mine_inc = 0.05
    rows = 28
    cols = 30
    window_width = Constants.BOARD_SQUARE_SIZE * cols
    board_height = Constants.BOARD_SQUARE_SIZE * rows


class GameControl:
    """Container for utilites to control the game

    Attributes:
        click_mode: Flag controlling how mouse events are handled.
        game_state: Flag controlling if the game is in progress.
        difficulty: Flag representing the current difficulty of the game.
        num_mines: Number of mines in the board.
        squares_to_win: Number of squares to uncover needed to win.
        squares_uncovered: Number of squares that have been uncovered.
        flags_placed: Number of flags placed on the board.
        seconds_elpased: Time elapsed playing the game, in seconds.
        on_hold: Flag controlling if the game is on hold, ie, creating a board.
        drag_mode: Flag controlling if clicking dragging adds or remove squares in board creation.

    """
    click_mode = ClickMode.UNCOVER
    game_state = GameState.PLAYING
    difficulty = Difficulty.EASY
    num_mines = 0
    squares_to_win = 0
    squares_uncovered = 0
    flags_placed = 0
    seconds_elpased = 0
    on_hold = True
    drag_mode = True

    @staticmethod
    def check_win() -> None:
        """Check if the game has been won, and executes winning sequence if so."""
        if GameControl.squares_uncovered == GameControl.squares_to_win:
            WindowControl.reset_button.config(im=Constants.BOARD_IMAGES[16])
            GameControl.game_state = GameState.DONE
            GameControl.flags_placed = GameControl.num_mines
            WindowControl.update_flag_counter()
            for square in WindowControl.board_frame.grid_slaves():
                if square.enabled and not square.uncovered and square.value < 0:
                    if square.value == -1:
                        square.config(im=Constants.BOARD_IMAGES[11])
                    else:
                        square.config(im=Constants.EXTENDED_BOARD_IMAGES[-square.value + 38])
            save_time = messagebox.askyesno(title='FreeForm Minesweeper', message='You Win!\nSave your time to the leaderboard?')
            if save_time:
                pass#GameControl.save_time_to_file()

    @staticmethod
    def has_lost() -> None:
        """Execute lsoing sequence."""
        WindowControl.reset_button.config(im=Constants.BOARD_IMAGES[15])
        GameControl.game_state = GameState.DONE
        for square in WindowControl.board_frame.grid_slaves():
            if square.enabled and not square.uncovered and not square.flagged and square.value == -1:
                square.config(im=Constants.BOARD_IMAGES[9])
            elif square.enabled and not square.uncovered and not square.flagged and square.value < -1:
                square.config(im=Constants.EXTENDED_BOARD_IMAGES[-square.value + 30])

            if square.flagged and square.value > -1:
                if square.num_flags == 1:
                    square.config(im=Constants.BOARD_IMAGES[12])
                elif square.num_flags > 1:
                    square.config(im=Constants.EXTENDED_BOARD_IMAGES[square.num_flags + 42])
            elif square.flagged and square.value <= -1 and square.num_flags != -square.value:
                if square.num_flags == 1:
                    square.config(im=Constants.BOARD_IMAGES[12])
                elif square.num_flags > 1:
                    square.config(im=Constants.EXTENDED_BOARD_IMAGES[square.num_flags + 42])

    @staticmethod
    def play_game() -> None:
        """Core gameplay loop when it is being played as Minesweeper, or a variant."""
        WindowControl.root.unbind('<Control-i>')
        if Options.flagless:
            WindowControl.mode_switch_button.config(state='disabled')
        else:
            WindowControl.root.bind('<Control-f>', lambda event: GameControl.switch_mode())
            WindowControl.mode_switch_button.bind('<ButtonPress-1>', lambda event: GameControl.switch_mode())

        local_diff = GameControl.difficulty.value + Options.multimine_mine_inc if Options.multimines else GameControl.difficulty.value
        num_squares = sum([1 if sq.enabled else 0 for sq in WindowControl.board_frame.grid_slaves()])

        GameControl.squares_uncovered = 0
        GameControl.flags_placed = 0
        GameControl.seconds_elpased = 0
        if GameControl.click_mode is ClickMode.FLAG:
            GameControl.switch_mode()
        GameControl.on_hold = False

        squares = WindowControl.board_frame.grid_slaves()

        GameControl.num_mines = min(int(num_squares * local_diff), 999)
        seed_mines = (GameControl.num_mines // 2) if Options.multimines else GameControl.num_mines
        wave_mines = GameControl.num_mines - seed_mines
        seed_mines_placed = 0
        wave_mines_placed = 0

        while seed_mines_placed < seed_mines:
            sq = random.choice(squares)
            if sq.enabled and not sq.value:
                sq.value -= 1
                seed_mines_placed += 1

        while wave_mines_placed < wave_mines:
            sq = random.choice(squares)
            if sq.enabled and not sq.value:
                if random.random() < 1 - Options.multimine_sq_inc:
                    sq.value -= 1
                    wave_mines_placed += 1
            elif sq.enabled and sq.value:
                if sq.value != -5:
                    sq.value -= 1
                    wave_mines_placed += 1

        squares_with_mines = 0
        for sq in squares:
            if sq.value < 0:
                squares_with_mines += 1

        GameControl.squares_to_win = num_squares - squares_with_mines

        for sq in squares:
            sq.lock()
            sq.link_to_neighbours()
            sq.unbind('<B1-Motion>')
            sq.bind('<Button-1>', lambda event, square=sq: square.uncover())
            if not(Options.flagless or Options.multimines):
                sq.bind('<Button-3>', lambda event, square=sq: square.flag())
            sq.bind('<Double-Button-1>', lambda event, square=sq: square.chord())

        WindowControl.reset_button.bind('<ButtonPress-1>', lambda event: WindowControl.reset_button.config(im=Constants.BOARD_IMAGES[14]))
        WindowControl.reset_button.bind('<ButtonRelease-1>', lambda event: GameControl.reset_game())
        options = WindowControl.play_button.grid_info()
        WindowControl.play_button.grid_remove()
        WindowControl.stop_button.grid(**options)
        btns = chain(
            WindowControl.diff_frame.grid_slaves(),
            WindowControl.controls_frame.grid_slaves(),
            WindowControl.presets_frame.grid_slaves(),
            (WindowControl.settings_button,)
        )
        for btn in btns:
            if isinstance(btn, tk.Button):
                btn.config(state='disabled')

        WindowControl.update_flag_counter()
        GameControl.switch_mode()
        GameControl.switch_mode()
        GameControl.game_state = GameState.PLAYING

    @staticmethod
    def reset_game() -> None:
        """Display dialouge prompt to start a new game, and reset if confirmed."""
        if GameControl.game_state is GameState.PLAYING:
            reset = messagebox.askyesno(
                title='Reset Game?',
                message='Are you sure you want to start a new game?',
                default=messagebox.NO
            )
            if not reset:
                return
        GameControl.game_state = GameState.DONE
        WindowControl.reset_button.unbind('<ButtonPress-1>')
        WindowControl.reset_button.unbind('<ButtonRelease-1>')
        WindowControl.mode_switch_button.unbind('<ButtonPress-1>')
        WindowControl.reset_timer()
        WindowControl.reset_button.config(im=Constants.BOARD_IMAGES[13])
        for square in WindowControl.board_frame.grid_slaves():
            if square.enabled:
                square.reset()
        if not GameControl.on_hold:
            GameControl.play_game()

    @staticmethod
    def stop_game() -> None:
        """Display dialouge prompt to stop the current game, and place game on hold if confirmed."""
        if GameControl.game_state is GameState.PLAYING:
            stop = messagebox.askyesno(
                title='Stop Playing?',
                message='Are you sure you want to stop playing?',
                default=messagebox.NO
            )
            if not stop:
                return
        GameControl.game_state = GameState.DONE
        GameControl.on_hold = True
        WindowControl.root.bind('<Control-i>', lambda event: GameControl.invert_board())
        WindowControl.root.unbind('<Control-f>')
        WindowControl.reset_button.unbind('<ButtonPress-1>')
        WindowControl.reset_button.unbind('<ButtonRelease-1>')
        WindowControl.mode_switch_button.unbind('<ButtonPress-1>')
        WindowControl.mode_switch_button.config(im=Constants.BOARD_IMAGES[17])
        GameControl.reset_game()
        WindowControl.reset_timer()
        WindowControl.reset_flag_counter()
        options = WindowControl.stop_button.grid_info()
        WindowControl.stop_button.grid_remove()
        WindowControl.play_button.grid(**options)
        btns = chain(
            WindowControl.diff_frame.grid_slaves(),
            WindowControl.controls_frame.grid_slaves(),
            WindowControl.presets_frame.grid_slaves(),
            (WindowControl.settings_button,)
        )
        for btn in btns:
            if isinstance(btn, tk.Button):
                btn.config(state='normal')
        if Options.flagless:
            WindowControl.mode_switch_button.config(state='normal')
        for sq in WindowControl.board_frame.grid_slaves():
            sq.unlock()
            sq.bind('<Button-1>', lambda event, square=sq: square.toggle_enable())
            sq.bind('<B1-Motion>', lambda event, square=sq: WindowControl.drag_enable_toggle(event, square))
            sq.unbind('<Double-Button-1>')

    @staticmethod
    def change_difficulty(difficulty: Difficulty, btn_pressed: tk.Button) -> None:
        """Change the difficulty of the game.

        Args:
            difficulty: The new difficulty to apply.
            btn_pressed: The button pressed corresponding to the difficulty.

        """
        GameControl.difficulty = difficulty
        for diff_btn in WindowControl.diff_frame.grid_slaves():
            if isinstance(diff_btn, tk.Button):
                diff_btn.config(relief='raised', bg=Constants.DEFAULT_COLOUR)
        btn_pressed.config(relief='sunken', bg=Constants.BACKGROUND_COLOUR)

    @staticmethod
    def fill_board() -> None:
        """Make all squares enabled."""
        for sq in WindowControl.board_frame.grid_slaves():
            if not sq.enabled:
                sq.toggle_enable()

    @staticmethod
    def clear_board() -> None:
        """Make all squares disabled."""
        for sq in WindowControl.board_frame.grid_slaves():
            if sq.enabled:
                sq.toggle_enable()

    @staticmethod
    def switch_mode() -> None:
        """Switch the effect clcking has a square during the game."""
        if GameControl.click_mode is ClickMode.UNCOVER:
            GameControl.click_mode = ClickMode.FLAG
            WindowControl.mode_switch_button.config(im=Constants.BOARD_IMAGES[18])
            for sq in WindowControl.board_frame.grid_slaves():
                if Options.multimines:
                    sq.bind('<Button-1>', lambda event, square=sq: square.add_flag())
                    sq.bind('<Button-3>', lambda event, square=sq: square.remove_flag())
                    sq.bind('<Double-Button-1>', lambda event, square=sq: square.add_flag(), add='+')
                else:
                    sq.bind('<Button-1>', lambda event, square=sq: square.flag())
        else:
            GameControl.click_mode = ClickMode.UNCOVER
            WindowControl.mode_switch_button.config(im=Constants.BOARD_IMAGES[17])
            for sq in WindowControl.board_frame.grid_slaves():
                sq.bind('<Button-1>', lambda event, square=sq: square.uncover())
                if Options.multimines:
                    sq.unbind('<Button-3>')
                    sq.unbind('<Double-Button-1>')
                    sq.bind('<Double-Button-1>', lambda event, square=sq: square.chord())

    @staticmethod
    def compress_board() -> list[str]:
        """Compress the current board to its smallest possible form."""
        # Keep track of the leftmost enabled square. Set to the right side of the field
        leftmost = Options.cols - 1
        # Will be the final bit mapping of the board
        board_bits = []
        # A flag for detecting when the first row with an enabled square is hit
        reached_content = False
        # Iterate over the number rows of the field
        for row in range(Options.rows):
            # Define an empty string that will represent the bits in a row
            bit_row = ''
            # Iterate over the number of columns in the field
            for col in range(Options.cols):
                # Get the square at the current position
                square = WindowControl.board_frame.grid_slaves(row=row, column=col)[0]
                # Set the next bit in the row to be 1 if the square is enabled and 0 if it is not
                bit_row += '1' if square.enabled else '0'
            # If the bit row contains 1
            if '1' in bit_row:
                # Get the index of the first and last 1 in the bit row
                leftmost_index = bit_row.index('1')
                rightmost_index = bit_row.rindex('1') + 1
                # Set the leftmost index to the minimum of the current and the left index just calculated
                leftmost = min(leftmost_index, leftmost)
                # Set the flag that we've reached a row with content
                reached_content = True
                # Append the bit row from the beginning to the rightmost index. This trims off all the ending 0 in the bit row
                board_bits.append(bit_row[:rightmost_index])
            # Otherwise, if the bit row has no 1 but is in the content of the board
            elif '1' not in bit_row and reached_content:
                # Set the row to be 0 to represent the empty row in the middle of the field
                board_bits.append('0')
        # Get the index of the last row of content. Set to the bottom of the field
        last_content_index = len(board_bits)
        # Starting from the bottom, loop over the rows of the board
        for i, row in enumerate(reversed(board_bits)):
            # When a row is hit that has content, all the empty rows at the bottom have been iterated through
            if '1' in row:
                # So set the index of the last row of content to this spot and exit the loop
                last_content_index -= i
                break
        # Trim the trailing rows of 0 off the end
        board_bits = board_bits[:last_content_index]
        # Go through the rows of the board
        for i, row in enumerate(board_bits):
            # If the row isn't a filler empty row in the middle of the field
            if row != '0':
                # Trim the bigging of the row from the index of the leftmost enabled square
                board_bits[i] = row[leftmost:]
        # At this point the board is saved as rows of bits that has been trimmed down to the smallest possible dimensions of the board
        return board_bits

    @staticmethod
    def save_board() -> None:
        """Save the current board to a file."""
        compressed_board = GameControl.compress_board()
        board_file = filedialog.asksaveasfilename(
            initialdir=Constants.SAVE_LOAD_DIR, title='Save Board',
            filetypes=Constants.FILE_TYPE, defaultextension=Constants.FILE_EXTENSION
        )
        if not board_file:
            return
        if not board_file.endswith(Constants.FILE_EXTENSION):
            messagebox.showerror(
                title='Extension Error',
                message=f'Invalid extension for FreeForm Minesweeper board ({"".join(board_file.partition(".")[1:])}).'
            )
            return
        try:
            with open(board_file, 'w') as board_save_file:
                board_save_file.write('\n'.join(compressed_board))
                board_save_file.write('\n')
        except Exception:
            messagebox.showerror(title='Saving Error', message='Was not able to save the file.')

    @staticmethod
    def load_board(filename: Optional[str] = None) -> None:
        """Load an external board into the game.

        Args:
            filename: Name of the board file to load.

        """
        board_file = filename or filedialog.askopenfilename(initialdir=Constants.SAVE_LOAD_DIR, title='Open Board', filetypes=Constants.FILE_TYPE)
        if not board_file:
            return
        try:
            with open(board_file, 'r') as board_load_file:
                board_bits = [line.strip() for line in board_load_file.readlines()]
        except Exception:
            messagebox.showerror(title='Opening Error', message='Was not able to open the file.')
            return
        if len(board_bits) > Options.rows or len(max(board_bits, key=len)) > Options.cols:
            messagebox.showerror(title='Loading Error', message='Board was too large to be loaded properly.')
            return
        GameControl.clear_board()
        for curr_row, bit_row in enumerate(board_bits):
            for curr_col, bit in enumerate(bit_row):
                if bit == '1':
                    WindowControl.board_frame.grid_slaves(row=curr_row, column=curr_col)[0].toggle_enable()

    @staticmethod
    def invert_board() -> None:
        """Toggle all the squares on the board betwixt enabled and disabled."""
        for sq in WindowControl.board_frame.grid_slaves():
            sq.toggle_enable()

    @staticmethod
    def save_time_to_file(filename: str = Constants.LEADERBOARD_FILENAME) -> None:
        """Save the completion time for the current board to the leaderboard file.

        Args:
            filename (optional): File path to save time to. Defaults to `Constants.LEADERBOARD_FILENAME`.
        """
        name = tk.StringVar(value='')
        player = tk.StringVar(value='')

        name_player_entry_root = tk.Toplevel()
        name_player_entry_root.title('Save to Leaderboard')
        name_player_entry_root.resizable(0, 0)
        if get_os() == 'Windows':
            name_player_entry_root.iconbitmap(Constants.LEADERBOARD_ICON_ICO)
        elif get_os() == 'Linux':
            name_player_entry_root.iconphoto(False, Constants.LEADERBOARD_ICON_PNG)
        
        name_player_frame = tk.Frame(name_player_entry_root, bg=Constants.BACKGROUND_COLOUR, width=280, height=200)
        name_player_frame.grid_propagate(False)
        
        name_label = tk.Label(name_player_frame, text='Name This Board', font=Constants.FONT_BIG, bg=Constants.BACKGROUND_COLOUR)
        name_entry = tk.Entry(name_player_frame, exportselection=False, font=Constants.FONT_BIG, textvariable=name)
        
        player_label = tk.Label(name_player_frame, text='Your Name', font=Constants.FONT_BIG, bg=Constants.BACKGROUND_COLOUR)
        player_entry = tk.Entry(name_player_frame, exportselection=False, font=Constants.FONT_BIG, textvariable=player)
        
        save_button = tk.Button(name_player_frame, text='Save Time', font=Constants.FONT_BIG)
        
        name_player_frame.grid(row=0, column=0)
        
        name_label.grid(row=1, column=0)
        name_entry.grid(row=2, column=0, padx=6)
       
        player_label.grid(row=3, column=0)
        player_entry.grid(row=4, column=0, padx=6)
        
        save_button.grid(row=5, column=0, pady=6)

        
        current_compressed_board = GameControl.compress_board()
        board_str = 'N'.join(current_compressed_board)
        leaderboard_id = board_str.replace('1', 'S').replace('0', 'E')
        leaderboard_id = ''.join(str(len(list(g)))+k for k, g in groupby(leaderboard_id))
        # print(leaderboard_id)

        


class BoardSquare(tk.Label):
    """A toggable square used in playing Minesweeper.

    Args:
        master: Parent widget.
        size: Dimensions, in pixels.
        tk_image: Image displayed in square.

    Attributes:
        master: Parent widget
        image: Image displayed in square.
        uncovered: Flag for if the square has been uncovered.
        flagged: Flag for if the square has been flagged.
        enabled: Flag if the square is enabled to use in game.
        num_flags: Number of flags on the square.
        value: Number in the square.
        directions: 8 main directions.
        neighbours: Neighbouring squares, in each of the 8 directions.

    """
    def __init__(self, master: tk.Widget, size: int, tk_image: tk.PhotoImage) -> None:
        super().__init__(master, height=size, width=size, im=tk_image, bd=0)
        self.master = master
        self.image = tk_image
        self.uncovered = False
        self.flagged = False
        self.enabled = True
        self.num_flags = 0
        self.value = 0
        self.directions = ('nw', 'n', 'ne', 'w', 'e', 'sw', 's', 'se')
        self.neighbours = dict.fromkeys(self.directions)

    def link_to_neighbours(self) -> None:
        """Find and store all neighbouring squares"""
        grid_x = self.grid_info()['row']
        grid_y = self.grid_info()['column']
        directions = list(self.directions)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not i and not j:
                    continue
                curr_direction = directions.pop(0)
                check_x = i + grid_x
                check_y = j + grid_y
                if check_x >= 0 and check_y >= 0:
                    try:
                        child_widget = self.master.grid_slaves(row=check_x, column=check_y)[0]
                    except IndexError:
                        pass
                    else:
                        if isinstance(child_widget, BoardSquare) and child_widget.enabled:
                            self.neighbours[curr_direction] = child_widget

    def uncover(self) -> None:
        """Uncover the square."""
        if not self.enabled or GameControl.game_state is GameState.DONE:
            return
        if not self.uncovered and not self.flagged:
            if self.value > -1:
                self.uncovered = True
                GameControl.squares_uncovered += 1
                mines_around = 0
                for neighbour in self.neighbours.values():
                    if neighbour is not None and neighbour.value <= -1:
                        mines_around -= neighbour.value
                self.value = mines_around
                if mines_around < 9:
                    self.image = Constants.BOARD_IMAGES[self.value]
                else:
                    self.image = Constants.EXTENDED_BOARD_IMAGES[self.value - 9]
                self.config(im=self.image)
                if not self.value:
                    for neighbour in self.neighbours.values():
                        if neighbour is not None and not neighbour.flagged:
                            neighbour.uncover()
            else:
                if Options.grace_rule and GameControl.squares_uncovered == 0:
                    GameControl.reset_game()
                    self.uncover()
                    return
                if GameControl.game_state is GameState.PLAYING:
                    GameControl.has_lost()
                if self.value == -1:
                    self.image = Constants.BOARD_IMAGES[10]
                elif self.value < -1:
                    self.image = Constants.EXTENDED_BOARD_IMAGES[-self.value + 34]
                self.config(im=self.image)
        GameControl.check_win()

    def flag(self) -> None:  # For normal gameplay
        """Toggle a flag on the square."""
        if not self.enabled or self.uncovered or GameControl.game_state is GameState.DONE:
            return
        if not self.flagged and GameControl.flags_placed < GameControl.num_mines:
            self.flagged = not self.flagged
            self.num_flags = 1
            self.image = Constants.BOARD_IMAGES[11]
            self.config(im=self.image)
            GameControl.flags_placed += 1
        elif self.flagged:
            self.flagged = not self.flagged
            self.num_flags = 0
            self.image = Constants.BOARD_IMAGES[20]
            self.config(im=self.image)
            GameControl.flags_placed -= 1
        WindowControl.update_flag_counter()

    def add_flag(self) -> None:  # For multimine
        """Add a flag to the square."""
        if not self.enabled or self.uncovered or GameControl.game_state is GameState.DONE:
            return
        if self.num_flags < 5 and GameControl.flags_placed < GameControl.num_mines:
            self.num_flags += 1
            self.flagged = True
            GameControl.flags_placed += 1
            if self.num_flags == 1:
                self.image = Constants.BOARD_IMAGES[11]
            else:
                self.image = Constants.EXTENDED_BOARD_IMAGES[self.num_flags + 38]
            self.config(im=self.image)
        WindowControl.update_flag_counter()

    def remove_flag(self) -> None:  # For multimine
        """Remove a flag from the square."""
        if not self.enabled or self.uncovered or GameControl.game_state is GameState.DONE:
            return
        if self.num_flags > 0:
            self.num_flags -= 1
            GameControl.flags_placed -= 1
            if self.num_flags == 1:
                self.image = Constants.BOARD_IMAGES[11]
            elif self.num_flags == 0:
                self.image = Constants.BOARD_IMAGES[20]
                self.flagged = False
            else:
                self.image = Constants.EXTENDED_BOARD_IMAGES[self.num_flags + 38]
            self.config(im=self.image)
        WindowControl.update_flag_counter()

    def chord(self) -> None:
        """Chord the square (click all the squares around it if appropriate)."""
        if not self.enabled or GameControl.game_state is GameState.DONE:
            return
        if self.uncovered and not self.flagged:
            flags_around = 0
            for neighbour in self.neighbours.values():
                if neighbour is not None and neighbour.flagged:
                    flags_around += neighbour.num_flags
            if flags_around == self.value:
                for neighbour in self.neighbours.values():
                    if neighbour is not None and not neighbour.flagged:
                        neighbour.uncover()

    def toggle_enable(self) -> None:
        """Toggle square betwixt enabled and disabled"""
        if self.enabled:
            self.config(im=Constants.UNLOCKED_BLACK_SQUARE)
        else:
            self.config(im=self.image)
        self.enabled = not self.enabled

    def lock(self) -> None:
        """Lock the square so it can't be toggled."""
        if not self.enabled:
            self.config(im=Constants.LOCKED_BLACK_SQUARE)

    def unlock(self) -> None:
        """Unlock the square so it can be toggled."""
        if not self.enabled:
            self.config(im=Constants.UNLOCKED_BLACK_SQUARE)

    def reset(self) -> None:
        """Reset the square back to base initialization"""
        self.image = Constants.BOARD_IMAGES[20]
        self.config(im=self.image)
        self.uncovered = False
        self.flagged = False
        self.num_flags = 0
        self.enabled = True
        self.value = 0
        self.neighbours = dict.fromkeys(self.directions)


class WindowControl:
    """Utility class containing the window objects and related funuctions.

    Attributes:
        root: Main window of the program.
        main_frame: Primary frame all other widgets reside in.
        menu_frame: Frame all control widgets reside in.
        board_frame: Frame all squares of the board reside in.
        mswpr_frame: Frame to group various game widgets.
        presets_frame: Frame to group preset widgets.
        diff_frame: Frame to group difficulty widgets.
        timer_frame: Frame to group timer widgets.
        flags_frame: Frame to group flag widgets.
        controls_frame: Frame to group control widgets.
        reset_button: Game reset button.
        mode_switch_button: Click mode switch button.
        settings_button: Settings button.
        play_button: Play game button.
        stop_button: Stop game button.

    """
    root = tk.Tk()
    main_frame = tk.Frame(
        root, width=Options.window_width,
        height=Options.board_height + Constants.SEGMENT_HEIGHT + 4 * Constants.PADDING_DIST, bg='black'
    )
    menu_frame = tk.Frame(
        main_frame, width=Options.window_width, height=Constants.SEGMENT_HEIGHT + 4 * Constants.PADDING_DIST,
        bg=Constants.BACKGROUND_COLOUR
    )
    board_frame = tk.Frame(
        main_frame, width=Options.window_width, height=Options.board_height,
        bg=Constants.BACKGROUND_COLOUR
    )

    mswpr_frame = tk.Frame(menu_frame, bg=Constants.BACKGROUND_COLOUR)
    presets_frame = tk.Frame(menu_frame, bg=Constants.BACKGROUND_COLOUR)
    diff_frame = tk.Frame(menu_frame, bg=Constants.BACKGROUND_COLOUR)
    timer_frame = tk.Frame(menu_frame, bg=Constants.BACKGROUND_COLOUR)
    flags_frame = tk.Frame(menu_frame, bg=Constants.BACKGROUND_COLOUR)
    controls_frame = tk.Frame(menu_frame, bg=Constants.BACKGROUND_COLOUR)

    reset_button = tk.Label(mswpr_frame, width=Constants.BOARD_SQUARE_SIZE, height=Constants.BOARD_SQUARE_SIZE, bd=0)
    mode_switch_button = tk.Label(mswpr_frame, width=Constants.BOARD_SQUARE_SIZE, height=Constants.BOARD_SQUARE_SIZE, bd=0)
    settings_button = tk.Button(mswpr_frame, width=Constants.BOARD_SQUARE_SIZE, height=Constants.BOARD_SQUARE_SIZE, bd=0)
    play_button = tk.Button(mswpr_frame, text='Play', font=Constants.FONT, width=5, command=GameControl.play_game)
    stop_button = tk.Button(mswpr_frame, text='Stop', font=Constants.FONT, width=5, command=GameControl.stop_game)

    @staticmethod
    def init_window() -> None:
        """Initialize window widgets."""
        WindowControl.root.resizable(0, 0)
        WindowControl.root.title('FreeForm Minesweeper')
        WindowControl.root.bind('<Control-i>', lambda event: GameControl.invert_board())
        WindowControl.main_frame.grid_propagate(0)
        WindowControl.menu_frame.grid_propagate(0)
        WindowControl.board_frame.grid_propagate(0)
        for i in range(6):
            WindowControl.menu_frame.grid_columnconfigure(i, weight=1)
        WindowControl.menu_frame.grid(row=0, column=0, sticky='nsew')
        WindowControl.board_frame.grid(row=1, column=0, sticky='nsew')
        WindowControl.main_frame.grid(row=2, column=0, sticky='nsew')

    @staticmethod
    def init_board() -> None:
        """Initialize board widgets."""
        for i in range(Options.rows):
            WindowControl.board_frame.grid_rowconfigure(i, minsize=Constants.BOARD_SQUARE_SIZE, weight=1)
        for i in range(Options.cols):
            WindowControl.board_frame.grid_columnconfigure(i, minsize=Constants.BOARD_SQUARE_SIZE, weight=1)
        for x in range(Options.rows):
            for y in range(Options.cols):
                sq = BoardSquare(WindowControl.board_frame, Constants.BOARD_SQUARE_SIZE, Constants.BOARD_IMAGES[20])
                sq.toggle_enable()
                sq.bind('<Button-1>', lambda event, square=sq: square.toggle_enable())
                sq.bind('<B1-Motion>', lambda event, square=sq: WindowControl.drag_enable_toggle(event, square))
                sq.grid(row=x, column=y, sticky='nsew')

    @staticmethod
    def init_menu() -> None:
        """Initialize menu widgets."""
        preset_easy = tk.Button(
            WindowControl.presets_frame, text='Easy', font=Constants.FONT, width=6,
            command=lambda: GameControl.change_difficulty(Difficulty.EASY, diff_1) or GameControl.load_board('presets/easy.ffmnswpr')
        )
        preset_medium = tk.Button(
            WindowControl.presets_frame, text='Medium', font=Constants.FONT, width=6,
            command=lambda: GameControl.change_difficulty(Difficulty.MEDIUM, diff_2) or GameControl.load_board('presets/medium.ffmnswpr')
        )
        preset_hard = tk.Button(
            WindowControl.presets_frame, text='Hard', font=Constants.FONT, width=6,
            command=lambda: GameControl.change_difficulty(Difficulty.HARD, diff_3) or GameControl.load_board('presets/hard.ffmnswpr')
        )
        preset_expert = tk.Button(
            WindowControl.presets_frame, text='Expert', font=Constants.FONT, width=6,
            command=lambda: GameControl.change_difficulty(Difficulty.EXPERT, diff_4) or GameControl.load_board('presets/expert.ffmnswpr')
        )
        preset_easy.grid(row=0, column=0, sticky='nsew')
        preset_medium.grid(row=0, column=1, sticky='nsew')
        preset_hard.grid(row=1, column=0, sticky='nsew')
        preset_expert.grid(row=1, column=1, sticky='nsew')
        WindowControl.presets_frame.grid(row=0, column=0)

        flag_left = tk.Label(WindowControl.flags_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        flag_mid = tk.Label(WindowControl.flags_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        flag_right = tk.Label(WindowControl.flags_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        flag_left.grid(row=0, column=0, sticky='nsew')
        flag_mid.grid(row=0, column=1, sticky='nsew')
        flag_right.grid(row=0, column=2, sticky='nsew')
        WindowControl.flags_frame.grid(row=0, column=1)

        WindowControl.mode_switch_button.config(im=Constants.BOARD_IMAGES[17])
        WindowControl.reset_button.config(im=Constants.BOARD_IMAGES[13])
        WindowControl.settings_button.config(im=Constants.BOARD_IMAGES[19], command=WindowControl.settings_window)
        WindowControl.mode_switch_button.grid(row=0, column=0, sticky='nsew')
        WindowControl.reset_button.grid(row=0, column=1, padx=Constants.PADDING_DIST, pady=3, sticky='nsew')
        WindowControl.settings_button.grid(row=0, column=2, sticky='nsew')
        WindowControl.play_button.grid(row=1, column=0, columnspan=3, sticky='nsew')
        WindowControl.mswpr_frame.grid(row=0, column=2)

        timer_left = tk.Label(WindowControl.timer_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        timer_mid = tk.Label(WindowControl.timer_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        timer_right = tk.Label(WindowControl.timer_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        timer_left.grid(row=0, column=0, sticky='nsew')
        timer_mid.grid(row=0, column=1, sticky='nsew')
        timer_right.grid(row=0, column=2, sticky='nsew')
        WindowControl.timer_frame.grid(row=0, column=3)

        diff_label = tk.Label(WindowControl.diff_frame, text='Difficulty', font=Constants.FONT, bg=Constants.BACKGROUND_COLOUR)
        diff_1 = tk.Button(
            WindowControl.diff_frame, text='1', font=Constants.FONT,
            command=lambda diff=Difficulty.EASY: GameControl.change_difficulty(diff, diff_1)
        )
        diff_2 = tk.Button(
            WindowControl.diff_frame, text='2', font=Constants.FONT,
            command=lambda diff=Difficulty.MEDIUM: GameControl.change_difficulty(diff, diff_2)
        )
        diff_3 = tk.Button(
            WindowControl.diff_frame, text='3', font=Constants.FONT,
            command=lambda diff=Difficulty.HARD: GameControl.change_difficulty(diff, diff_3)
        )
        diff_4 = tk.Button(
            WindowControl.diff_frame, text='4', font=Constants.FONT,
            command=lambda diff=Difficulty.EXPERT: GameControl.change_difficulty(diff, diff_4)
        )
        diff_label.grid(row=0, column=1, columnspan=4, sticky='nsew')
        diff_1.grid(row=1, column=1, sticky='nsew')
        diff_2.grid(row=1, column=2, sticky='nsew')
        diff_3.grid(row=1, column=3, sticky='nsew')
        diff_4.grid(row=1, column=4, sticky='nsew')
        WindowControl.diff_frame.grid(row=0, column=4)

        fill_button = tk.Button(WindowControl.controls_frame, text='Fill', font=Constants.FONT, width=5, command=GameControl.fill_board)
        clear_button = tk.Button(WindowControl.controls_frame, text='Clear', font=Constants.FONT, width=5, command=GameControl.clear_board)
        save_board_button = tk.Button(WindowControl.controls_frame, text='Save', font=Constants.FONT, width=5, command=lambda: GameControl.save_board())
        load_board_button = tk.Button(WindowControl.controls_frame, text='Load', font=Constants.FONT, width=5, command=lambda: GameControl.load_board())
        fill_button.grid(row=0, column=0, sticky='nsew')
        clear_button.grid(row=1, column=0, sticky='nsew')
        save_board_button.grid(row=0, column=1, sticky='nsew')
        load_board_button.grid(row=1, column=1, sticky='nsew')
        WindowControl.controls_frame.grid(row=0, column=5)

    @staticmethod
    def update_timer() -> None:
        """Update timer widgets."""
        if (GameControl.squares_uncovered or GameControl.flags_placed) and GameControl.game_state is GameState.PLAYING and not GameControl.on_hold:
            seconds = list(str(int(GameControl.seconds_elpased)).zfill(3))
            for number in WindowControl.timer_frame.grid_slaves():
                number.config(im=Constants.SEVSEG_IMAGES[int(seconds.pop())])

    @staticmethod
    def reset_timer() -> None:
        """Reset timer widgets."""
        for number in WindowControl.timer_frame.grid_slaves():
            number.config(im=Constants.SEVSEG_IMAGES[0])

    @staticmethod
    def update_flag_counter() -> None:
        """Update flag widgets."""
        flags = GameControl.num_mines - GameControl.flags_placed
        value_container = list(str(flags).zfill(3))
        for number in WindowControl.flags_frame.grid_slaves():
            number.config(im=Constants.SEVSEG_IMAGES[int(value_container.pop())])

    @staticmethod
    def reset_flag_counter() -> None:
        """Reset flag widgets."""
        for number in WindowControl.flags_frame.grid_slaves():
            number.config(im=Constants.SEVSEG_IMAGES[0])

    @staticmethod
    def drag_enable_toggle(event: tk.EventType.Motion, initial_square: BoardSquare) -> None:
        """Turn all squares under the mouse to a sate based on an inital square while dragging.

        Args:
            event: Mouse motion event.
            initial_square: The initial square the dragging began on.
        """
        x = (event.x_root - initial_square.master.winfo_rootx()) // Constants.BOARD_SQUARE_SIZE
        y = (event.y_root - initial_square.master.winfo_rooty()) // Constants.BOARD_SQUARE_SIZE
        GameControl.drag_mode = initial_square.enabled
        if x in range(Options.rows) and y in range(Options.cols):
            try:
                square = WindowControl.board_frame.grid_slaves(row=y, column=x)[0]
            except IndexError:
                return
            else:
                if square.enabled is not GameControl.drag_mode:
                    square.toggle_enable()

    @staticmethod
    def settings_window() -> None:
        """Create and display the settings window."""
        WindowControl.settings_button.config(state='disabled')
        WindowControl.play_button.config(state='disabled')
        settings_root = tk.Toplevel()
        settings_root.title('FreeForm Minesweeper Options')
        settings_root.resizable(0, 0)
        if get_os() == 'Windows':
            settings_root.iconbitmap(Constants.SETTINGS_ICON_ICO)
        elif get_os() == 'Linux':
            settings_root.iconphoto(False, Constants.SETTINGS_ICON_PNG)
        settings_root.config(bg=Constants.DEFAULT_COLOUR)

        def settings_root_close() -> None:
            """Return button states to normal upon window close."""
            try:
                WindowControl.settings_button.config(state='normal')
                WindowControl.play_button.config(state='normal')
            except Exception:
                pass

        settings_root.bind('<Destroy>', lambda event: settings_root_close())

        options_label = tk.Label(settings_root, text='Game Options', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        options_label.grid(row=0, column=0, pady=Constants.PADDING_DIST)

        grace_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        gracerule = tk.BooleanVar(settings_root, Options.grace_rule)
        grace_label = tk.Label(grace_frame, text='Grace Rule', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        grace_on_choice = tk.Radiobutton(
            grace_frame, text='On', font=Constants.FONT_BIG, variable=gracerule,
            value=True, bg=Constants.DEFAULT_COLOUR, bd=0
        )
        grace_off_choice = tk.Radiobutton(
            grace_frame, text='Off', font=Constants.FONT_BIG, variable=gracerule,
            value=False, bg=Constants.DEFAULT_COLOUR, bd=0
        )
        grace_label.pack(anchor='w')
        grace_on_choice.pack(anchor='w')
        grace_off_choice.pack(anchor='w')
        grace_frame.grid(row=1, column=0, sticky='w', pady=Constants.PADDING_DIST)

        multimode = tk.BooleanVar(settings_root, Options.multimines)
        multi_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        multi_label = tk.Label(multi_frame, text='GameMode', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        normal_choice = tk.Radiobutton(
            multi_frame, text='Normal Mode', font=Constants.FONT_BIG, variable=multimode,
            value=False, bg=Constants.DEFAULT_COLOUR, bd=0
        )
        multi_choice = tk.Radiobutton(
            multi_frame, text='MultiMine Mode', font=Constants.FONT_BIG, variable=multimode,
            value=True, bg=Constants.DEFAULT_COLOUR, bd=0
        )
        multi_label.pack(anchor='w')
        normal_choice.pack(anchor='w')
        multi_choice.pack(anchor='w')
        multi_frame.grid(row=2, column=0, sticky='w', pady=Constants.PADDING_DIST)

        mines = tk.DoubleVar(settings_root, Options.multimine_mine_inc)
        mines_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        mines_label = tk.Label(mines_frame, text='MultiMine Mine Increase', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        mines_slider = tk.Scale(
            mines_frame, variable=mines, orient='horizontal', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR,
            resolution=0.01, from_=0.0, to=0.6, length=300, bd=0
        )
        mines_label.pack(anchor='w')
        mines_slider.pack()
        mines_frame.grid(row=3, column=0, sticky='w', pady=Constants.PADDING_DIST)

        density = tk.DoubleVar(settings_root, Options.multimine_sq_inc)
        density_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        density_label = tk.Label(density_frame, text='MultiMine Probability', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        density_slider = tk.Scale(
            density_frame, variable=density, orient='horizontal', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR,
            resolution=0.01, from_=0.1, to=0.9, length=300, bd=0
        )
        density_label.pack(anchor='w')
        density_slider.pack()
        density_frame.grid(row=4, column=0, sticky='w', pady=Constants.PADDING_DIST)

        flagless = tk.BooleanVar(settings_root, Options.flagless)
        flagless_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        flagless_label = tk.Label(flagless_frame, text='Flagless', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        flagless_on_choice = tk.Radiobutton(
            flagless_frame, text='Off', font=Constants.FONT_BIG, variable=flagless,
            value=False, bg=Constants.DEFAULT_COLOUR, bd=0
        )
        flagless_off_choice = tk.Radiobutton(
            flagless_frame, text='On', font=Constants.FONT_BIG, variable=flagless,
            value=True, bg=Constants.DEFAULT_COLOUR, bd=0
        )
        flagless_label.pack(anchor='w')
        flagless_off_choice.pack(anchor='w')
        flagless_on_choice.pack(anchor='w')
        flagless_frame.grid(row=5, column=0, sticky='w', pady=Constants.PADDING_DIST)

        rows = tk.IntVar(settings_root, Options.rows)
        rows_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        rows_label = tk.Label(rows_frame, text='Rows', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        rows_slider = tk.Scale(
            rows_frame, variable=rows, orient='horizontal', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR,
            resolution=1, from_=1, to=60, length=300, bd=0
        )
        rows_label.pack(anchor='w')
        rows_slider.pack()
        rows_frame.grid(row=6, column=0, sticky='w', pady=Constants.PADDING_DIST)

        columns = tk.IntVar(settings_root, Options.cols)
        columns_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        columns_label = tk.Label(rows_frame, text='Columns', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        columns_slider = tk.Scale(
            rows_frame, variable=columns, orient='horizontal', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR,
            resolution=1, from_=25, to=60, length=300, bd=0
        )
        columns_label.pack(anchor='w')
        columns_slider.pack()
        columns_frame.grid(row=6, column=0, sticky='w', pady=Constants.PADDING_DIST)

        def submit_vars() -> None:
            """Save options to the Options container class, and close the window."""
            Options.grace_rule = gracerule.get()
            Options.multimines = multimode.get()
            Options.multimine_mine_inc = mines.get()
            Options.flagless = flagless.get()
            Options.multimine_sq_inc = density.get()
            if rows.get() != Options.rows:
                Options.board_height = Constants.BOARD_SQUARE_SIZE * rows.get()
                WindowControl.main_frame.config(height=Options.board_height + Constants.SEGMENT_HEIGHT + 4 * Constants.PADDING_DIST)
                WindowControl.board_frame.config(height=Options.board_height)
            if columns.get() != Options.cols:
                Options.window_width = Constants.BOARD_SQUARE_SIZE * columns.get()
                WindowControl.main_frame.config(width=Options.window_width)
                WindowControl.menu_frame.config(width=Options.window_width)
                WindowControl.board_frame.config(width=Options.window_width)
            if rows.get() != Options.rows or columns.get() != Options.cols:
                Options.rows = rows.get()
                Options.cols = columns.get()
                for sq in WindowControl.board_frame.grid_slaves():
                    sq.destroy()
                WindowControl.init_board()
            settings_root.destroy()
            WindowControl.settings_button.config(state='normal')
            WindowControl.play_button.config(state='normal')

        submit_button = tk.Button(settings_root, text='Apply Settings', font=Constants.FONT, command=submit_vars)
        submit_button.grid(row=7, column=0, pady=Constants.PADDING_DIST)


def main() -> None:
    """Initialize all game components and run the mainloop."""
    WindowControl.init_window()
    Constants.init_board_images()
    Constants.init_sevseg_images()
    Constants.init_extended_board_images()
    Constants.init_window_icons()
    Constants.DEFAULT_COLOUR = WindowControl.root.cget('bg')
    if get_os() == 'Windows':
        WindowControl.root.iconbitmap(Constants.MAIN_ICON_ICO)
    elif get_os() == 'Linux':
        WindowControl.root.iconphoto(False, Constants.MAIN_ICON_PNG)
    WindowControl.init_menu()
    WindowControl.diff_frame.grid_slaves()[-2].invoke()
    WindowControl.init_board()
    if not MetaData.is_release_up_to_date():
        MetaData.outdated_notice()
    font.Font(name='TkCaptionFont', exists=True).config(family=Constants.FONT[0], size=Constants.FONT_BIG[1])
    WindowControl.root.bind('y', lambda e: GameControl.save_time_to_file())
    while True:
        try:
            WindowControl.root.update_idletasks()
            WindowControl.root.update()
        except tk.TclError:
            break
        else:
            time.sleep(Constants.MAINLOOP_TIME)
            if (GameControl.squares_uncovered or GameControl.flags_placed) and GameControl.game_state is GameState.PLAYING:
                GameControl.seconds_elpased = min(round(GameControl.seconds_elpased + Constants.MAINLOOP_TIME, 2), 999)
                if int(GameControl.seconds_elpased) == GameControl.seconds_elpased:
                    WindowControl.update_timer()


if __name__ == '__main__':
    main()
