"""The game FreeForm Minesweeper, bundled with MultiMinesweeper mode.

Play the game by executing the file as a program, and have fun!
The only code intended to be executed is the main() function. Any other use may result in errors or other undefined behaviour.

"""
import csv
import random
import tkinter as tk
import time

from datetime import date
from enum import Enum, auto
from itertools import chain, groupby
from os.path import expanduser
from platform import system
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font as tkFont
from tkinter import simpledialog
from tkinter import ttk

import requests

from PIL import Image, ImageTk


class MetaData:
    """Provide variables and utilities for checking current release against the most up to date release.

    Attributes:
        github_api_releases_url (str): URL to fetch data from.
        github_releases_url (str): URL to releases page for project.
        platform (str): The OS of the system the program is running on.
        version (str): The version of the code, shipped with releases.

    """
    github_api_releases_url = 'https://api.github.com/repos/KittyKittyKitKat/FreeForm-Minesweeper/releases'
    github_releases_url = 'https://github.com/KittyKittyKitKat/FreeForm-Minesweeper/releases'
    platform = system()

    # This is a dummy value for the purpose of source code.
    # The releases will have the proper information contained within.
    # This information will directly correlate to the release info on GitHub.
    version = 'vX.X.X'

    @staticmethod
    def get_release_tags(url):
        """Fetch the releases tags from GitHub's repo API.

        Args:
            url (str): Url pointing to the API JSON for GitHub releases.

        Returns:
            list[str]: A list of all the release tags for the OS the game is running on.

        """
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
    def is_release_up_to_date():
        """Compare release to most up to date.

        Returns:
            bool: True if the version is the most recent, or is the development dummy version.

        """
        if MetaData.version == 'vX.X.X':
            return True
        tags = MetaData.get_release_tags(MetaData.github_api_releases_url)
        if tags == '':
            WindowControl.messagebox_open = True
            messagebox.showwarning(
                title='OS Fetching Error',
                message=(
                    'Could not retrieve operating system information to queue updates.\n'
                    'You can safely ignore this message.'
                )
            )
            WindowControl.messagebox_open = False
            return True
        up_to_date_release = tags[-1]
        current_release = MetaData.platform + '-' + MetaData.version
        return up_to_date_release == current_release

    @staticmethod
    def outdated_notice():
        """Display pop up message detailing release is out of date."""
        message = (
            f'This release is not up to date, '
            'and as such you may be missing out on important new features or bug fixes.\n'
            f'Please go to {MetaData.github_releases_url} to download and install the lastest release.'
        )
        WindowControl.messagebox_open = True
        messagebox.showwarning(
            title='Outdated Release',
            message=message
        )
        WindowControl.messagebox_open = False


class ClickMode(Enum):
    """Enum representing the current clicking mode of the game."""
    UNCOVER = auto()
    FLAG = auto()


class GameState(Enum):
    """Enum representing the current state of the game."""
    DONE = auto()
    PLAYING = auto()


class Difficulty(Enum):
    """Enum representing the difficulty values for the game, in percentages."""
    EASY = 0.13
    MEDIUM = 0.16
    HARD = 0.207
    EXPERT = 0.25


class Constants:
    """Container for various game constants.

    Data types listed are intended data types to be used after all objects have been initialized.
    Attributes:
        BOARD_IMAGES (list[tk.PhotoImage]): Sprites used for the base Minesweeper game.
        SEVSEG_IMAGES (list[tk.PhotoImage]): Sprites used for seven segment displays.
        EXTENDED_BOARD_IMAGES (list[tk.PhotoImage]): Sprites used for multimine mode.
        BOARD_SQUARE_SIZE (int): Size of a square on the board, in pixels.
        SEGMENT_HEIGHT (int): Height of a seven segment number, in pixels.
        SEGMENT_WIDTH (int): Width of a seven segment number, in pixels.
        PADDING_DIST (int): Padding distance to space various widgets, in pixels.
        BACKGROUND_COLOUR (str): Background colour of the window, in #rrggbb.
        DEFAULT_COLOUR (str): Default colour of the window, in #rrggbb.
        FONT (tkFont.Font): Smaller font used for in game text.
        FONT_BIG (tkFont.Font): Larger font used for in game text.
        MAINLOOP_TIME (float): Time spent sleeping in mainloop of game.
        LOCKED_BLACK_SQUARE (tk.PhotoImage): Sprite for a locked disabled square.
        UNLOCKED_BLACK_SQUARE (tk.PhotoImage): Sprite for an unlocked disabled square.
        FILE_EXTENSION (str): File extension used for saving and loading board files.
        FILE_TYPE (tuple[str, str]): File type and extension, for file dialogues.
        LEADERBOARD_FILENAME (str): Path to the leaderboard JSON used to save times.
        SAVE_LOAD_DIR (str): Default directory for saving and loading board files.
        MAIN_ICON_ICO (str): Path to main window icon, relatively.
        SETTINGS_ICON_ICO (str): Path to settings window icon, relatively.
        LEADERBOARD_ICON_ICO (str): Path to leaderboard window icon, relatively.
        MAIN_ICON_PNG (str): PNG image for main window icon.
        SETTINGS_ICON_PNG (str): PNG image for settings window icon.

    """
    BOARD_SQUARE_SIZE = 32
    SEGMENT_HEIGHT = 46
    SEGMENT_WIDTH = 26
    PADDING_DIST = 5
    MIN_ROWS = 1
    MIN_COLUMNS = 25
    MAX_ROWS = 60
    MAX_COLUMNS = 60
    BACKGROUND_COLOUR = '#c0c0c0'
    DEFAULT_COLOUR = '#d9d9d9'
    MAINLOOP_TIME = 0.01
    LOCKED_BLACK_SQUARE = Image.new('RGBA', size=(BOARD_SQUARE_SIZE, BOARD_SQUARE_SIZE), color=(0, 0, 0))
    UNLOCKED_BLACK_SQUARE = Image.new('RGBA', size=(BOARD_SQUARE_SIZE, BOARD_SQUARE_SIZE), color=(0, 0, 0))
    FILE_EXTENSION = '.ffmnswpr'
    FILE_TYPE = (('FreeForm Minesweeper Board', f'*{FILE_EXTENSION}'),)
    LEADERBOARD_FILENAME = 'assets/leaderboard.csv'
    SAVE_LOAD_DIR = expanduser('~/Desktop')
    MAIN_ICON_ICO = 'assets/icon_main.ico'
    SETTINGS_ICON_ICO = 'assets/icon_settings.ico'
    LEADERBOARD_ICON_ICO = 'assets/icon_leaderboard.ico'

    @staticmethod
    def init_board_images():
        """Initialize the images used for the game board.

        First the proper sprite is drawn on UNLOCKED_BLACK_SQUARE.
        Doing this procedurally keeps the spritesheet tidy.
        The board spritesheet is load and cut into the individual squares.
        All the PIL images are converted to PhotoImage objects for TKinter.
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
    def init_sevseg_images():
        """Initialize the images used for the seven segment displays.

        The seven segment spritesheet is load and cut into the individual numbers.
        All the PIL images are converted to PhotoImage objects for TKinter.
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
    def init_extended_board_images():
        """Initialize the images used for the multimine mode.

        The extended board spritesheet is load and cut into the individual squares.
        All the PIL images are converted to PhotoImage objects for TKinter.
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
    def init_window_icons():
        """Initialize the images used for the window icons.

        The PIL images are converted to PhotoImage objects for TKinter.
        """
        MAIN_ICON = ImageTk.PhotoImage(Image.open('assets/icon_main.png'))
        SETTINGS_ICON = ImageTk.PhotoImage(Image.open('assets/icon_settings.png'))
        LEADERBOARD_ICON = ImageTk.PhotoImage(Image.open('assets/icon_leaderboard.png'))
        setattr(Constants, 'MAIN_ICON_PNG', MAIN_ICON)
        setattr(Constants, 'SETTINGS_ICON_PNG', SETTINGS_ICON)
        setattr(Constants, 'LEADERBOARD_ICON_PNG', LEADERBOARD_ICON)

    @staticmethod
    def init_fonts():
        """Initialize the fonts used in the game.

        Searches if the included font exists and uses it. Defaults to Courier.
        """
        if 'Minesweeper' in tkFont.families():
            FONT = tkFont.Font(family='Minesweeper', size=7, weight=tk.NORMAL)
            FONT_BIG = tkFont.Font(family='Minesweeper', size=9, weight=tk.NORMAL)
        else:
            FONT = tkFont.Font(family='Courier', size=9, weight='bold')
            FONT_BIG = tkFont.Font(family='Courier', size=15, weight='bold')
        setattr(Constants, 'FONT', FONT)
        setattr(Constants, 'FONT_BIG', FONT_BIG)


class Options:
    """Container for utilities to customize the game

    Attributes:
        multimines (bool): Flag if the game is in multimine mode.
        grace_rule (bool): Flag if the grace rule is set.
        multimine_sq_inc (float): Probability of getting multimines buff.
        flagless (bool): Flag if the game is in flagless mode.
        multimine_mine_inc (float): Percentage mine increase in multimine mode.
        rows (int): Number of rows in the game space.
        cols (int): Number of columns in the game space.
        window_width (int): Width of the window, in pixels.
        board_height (int): Height of the game board, in pixels.

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
    """Container for utilities to control the game

    Attributes:
        click_mode (ClickMode): Flag controlling how mouse events are handled.
        game_state (GameState): Flag controlling if the game is in progress.
        difficulty (Difficulty): Flag representing the current difficulty of the game.
        num_mines (int): Number of mines in the board.
        squares_to_win (int): Number of squares to uncover needed to win.
        squares_uncovered (int): Number of squares that have been uncovered.
        flags_placed (int): Number of flags placed on the board.
        seconds_elapsed (int): Time elapsed playing the game, in seconds.
        on_hold (bool): Flag controlling if the game is on hold, ie, creating a board.
        drag_mode (bool): Flag controlling if clicking dragging adds or remove squares in board creation.

    """
    click_mode = ClickMode.UNCOVER
    game_state = GameState.PLAYING
    difficulty = Difficulty.EASY
    num_mines = 0
    squares_to_win = 0
    squares_uncovered = 0
    flags_placed = 0
    seconds_elapsed = 0
    on_hold = True
    drag_mode = True

    @staticmethod
    def check_win():
        """Check if the game has been won, and execute winning sequence if so."""
        if GameControl.squares_uncovered == GameControl.squares_to_win and GameControl.game_state is GameState.PLAYING:
            WindowControl.new_game_button.config(im=Constants.BOARD_IMAGES[16])
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
                GameControl.save_time_to_file()

    @staticmethod
    def has_lost():
        """Execute losing sequence."""
        WindowControl.new_game_button.config(im=Constants.BOARD_IMAGES[15])
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
    def play_game():
        """Core gameplay loop when it is being played as Minesweeper, or a variant."""
        squares = WindowControl.board_frame.grid_slaves()

        for sq in squares:
            if sq.enabled:
                break
        else:
            WindowControl.messagebox_open = True
            messagebox.showwarning(title='FreeForm Minesweeper', message='Cannot start a game with no active squares.')
            WindowControl.messagebox_open = False
            return

        WindowControl.game_root.unbind('<Control-i>')
        if Options.flagless:
            WindowControl.mode_switch_button.config(state=tk.DISABLED)
        else:
            WindowControl.game_root.bind('<Control-f>', lambda event: GameControl.switch_mode())
            WindowControl.mode_switch_button.bind('<ButtonPress-1>', lambda event: GameControl.switch_mode())

        local_diff = GameControl.difficulty.value + Options.multimine_mine_inc if Options.multimines else GameControl.difficulty.value
        num_squares = sum([1 if sq.enabled else 0 for sq in WindowControl.board_frame.grid_slaves()])

        GameControl.squares_uncovered = 0
        GameControl.flags_placed = 0
        GameControl.seconds_elapsed = 0
        if GameControl.click_mode is ClickMode.FLAG:
            GameControl.switch_mode()
        GameControl.on_hold = False

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

        WindowControl.new_game_button.bind('<ButtonPress-1>', lambda event: WindowControl.new_game_button.config(im=Constants.BOARD_IMAGES[14]))
        WindowControl.new_game_button.bind('<ButtonRelease-1>', lambda event: GameControl.new_game())
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
                btn.config(state=tk.DISABLED)

        WindowControl.update_flag_counter()
        GameControl.switch_mode()
        GameControl.switch_mode()
        GameControl.game_state = GameState.PLAYING

    @staticmethod
    def new_game():
        """Display dialogue prompt to start a new game, and start a new game if confirmed."""
        if GameControl.game_state is GameState.PLAYING and not GameControl.on_hold:
            WindowControl.messagebox_open = True
            reset = messagebox.askyesno(
                title='Reset Game?',
                message='Are you sure you want to start a new game?',
                default=messagebox.NO
            )
            if reset:
                WindowControl.new_game_button.config(im=Constants.BOARD_IMAGES[13])
                WindowControl.messagebox_open = False
                return
            else:
                WindowControl.messagebox_open = False
        GameControl.game_state = GameState.DONE
        WindowControl.new_game_button.unbind('<ButtonPress-1>')
        WindowControl.new_game_button.unbind('<ButtonRelease-1>')
        WindowControl.mode_switch_button.unbind('<ButtonPress-1>')
        WindowControl.new_game_button.config(im=Constants.BOARD_IMAGES[13])
        WindowControl.reset_timer()
        for square in WindowControl.board_frame.grid_slaves():
            if square.enabled:
                square.reset()
        if not GameControl.on_hold:
            GameControl.play_game()

    @staticmethod
    def stop_game():
        """Display dialogue prompt to stop the current game, and place game on hold if confirmed."""
        if GameControl.game_state is GameState.PLAYING:
            WindowControl.messagebox_open = True
            stop = messagebox.askyesno(
                title='Stop Playing?',
                message='Are you sure you want to stop playing?',
                default=messagebox.NO
            )
            if not stop:
                WindowControl.messagebox_open = False
                return
            else:
                WindowControl.messagebox_open = False
        GameControl.game_state = GameState.DONE
        GameControl.on_hold = True
        WindowControl.game_root.bind('<Control-i>', lambda event: GameControl.invert_board())
        WindowControl.game_root.unbind('<Control-f>')
        WindowControl.new_game_button.unbind('<ButtonPress-1>')
        WindowControl.new_game_button.unbind('<ButtonRelease-1>')
        WindowControl.mode_switch_button.unbind('<ButtonPress-1>')
        WindowControl.mode_switch_button.config(im=Constants.BOARD_IMAGES[17])
        GameControl.new_game()
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
                btn.config(state=tk.NORMAL)
        if Options.flagless:
            WindowControl.mode_switch_button.config(state=tk.NORMAL)
        for sq in WindowControl.board_frame.grid_slaves():
            sq.unlock()
            sq.bind('<Button-1>', lambda event, square=sq: square.toggle_enable())
            sq.bind('<B1-Motion>', lambda event, square=sq: WindowControl.drag_enable_toggle(event, square))
            sq.unbind('<Double-Button-1>')

    @staticmethod
    def change_difficulty(difficulty: Difficulty, btn_pressed: tk.Button):
        """Change the difficulty of the game.

        Args:
            difficulty: The new difficulty to apply.
            btn_pressed: The button pressed corresponding to the difficulty.

        """
        GameControl.difficulty = difficulty
        for diff_btn in WindowControl.diff_frame.grid_slaves():
            if isinstance(diff_btn, tk.Button):
                diff_btn.config(relief=tk.RAISED, bg=Constants.DEFAULT_COLOUR)
        btn_pressed.config(relief=tk.SUNKEN, bg=Constants.BACKGROUND_COLOUR)

    @staticmethod
    def fill_board():
        """Make all squares enabled."""
        for sq in WindowControl.board_frame.grid_slaves():
            if not sq.enabled:
                sq.toggle_enable()

    @staticmethod
    def clear_board():
        """Make all squares disabled."""
        for sq in WindowControl.board_frame.grid_slaves():
            if sq.enabled:
                sq.toggle_enable()

    @staticmethod
    def switch_mode():
        """Switch the effect clicking has a square during the game."""
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
    def compress_board():
        """Compress the current board to its smallest possible form.

        Return
            list[str]: A list of binary strings representing a game board.

        """
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
    def compress_board_textually():
        """Compress board to it's smallest form using running length compression.

        Returns:
            str: Run length encoded string representing a game board.

        """
        board = 'N'.join(GameControl.compress_board()).replace('1', 'E').replace('0', 'D')
        return ''.join(str(len(list(g)))+k for k, g in groupby(board))

    @staticmethod
    def decompress_board_textually(txt_compressed_board):
        """Decompress a running length encoded board back into a list of binary strings.

        Args:
            txt_compressed_board (str): Run length encoded board.

        Returns:
            list[str]: A list of binary strings representing a game board.

        """
        decompressed_board = ''
        current_num = ''
        for char in txt_compressed_board:
            if char.isalpha():
                decompressed_board += char * int(current_num)
                current_num = ''
            else:
                current_num += char
        decompressed_board = decompressed_board.replace('E', '1').replace('D', '0').split('N')
        return decompressed_board

    @staticmethod
    def save_board():
        """Save the current board to a file."""
        compressed_board = GameControl.compress_board()
        board_file = filedialog.asksaveasfilename(
            initialdir=Constants.SAVE_LOAD_DIR, title='Save Board',
            filetypes=Constants.FILE_TYPE, defaultextension=Constants.FILE_EXTENSION
        )
        if not board_file:
            return
        if not board_file.endswith(Constants.FILE_EXTENSION):
            WindowControl.messagebox_open = True
            messagebox.showerror(
                title='Extension Error',
                message=f'Invalid extension for FreeForm Minesweeper board ({"".join(board_file.partition(".")[1:])}).'
            )
            WindowControl.messagebox_open = False
            return
        try:
            with open(board_file, 'w') as board_save_file:
                board_save_file.write('\n'.join(compressed_board))
                board_save_file.write('\n')
        except Exception:
            WindowControl.messagebox_open = True
            messagebox.showerror(title='Saving Error', message='Was not able to save the file.')
            WindowControl.messagebox_open = False

    @staticmethod
    def load_board(filename=None):
        """Load an external board into the game.

        Args:
            filename (str, optional): Name of the board file to load. Defaults to None.

        """
        board_file = filename or filedialog.askopenfilename(initialdir=Constants.SAVE_LOAD_DIR, title='Open Board', filetypes=Constants.FILE_TYPE)
        if not board_file:
            return
        try:
            with open(board_file, 'r') as board_load_file:
                board_bits = [line.strip() for line in board_load_file.readlines()]
        except Exception:
            WindowControl.messagebox_open = True
            messagebox.showerror(title='Opening Error', message='Was not able to open the file.')
            WindowControl.messagebox_open = False
            return
        if len(board_bits) > Options.rows or len(max(board_bits, key=len)) > Options.cols:
            WindowControl.messagebox_open = True
            messagebox.showerror(title='Loading Error', message='Board was too large to be loaded properly.')
            WindowControl.messagebox_open = False
            return
        GameControl.clear_board()
        for curr_row, bit_row in enumerate(board_bits):
            for curr_col, bit in enumerate(bit_row):
                if bit == '1':
                    WindowControl.board_frame.grid_slaves(row=curr_row, column=curr_col)[0].toggle_enable()

    @staticmethod
    def invert_board():
        """Toggle all the squares on the board betwixt enabled and disabled."""
        for sq in WindowControl.board_frame.grid_slaves():
            sq.toggle_enable()

    @staticmethod
    def save_time_to_file(filename=Constants.LEADERBOARD_FILENAME):
        """Save the completion time for the current board to the leaderboard file.

        Args:
            filename (str, optional): File path to save time to. Defaults to Constants.LEADERBOARD_FILENAME.

        """
        try:
            with open(filename, newline='') as read_fp:
                reader = csv.DictReader(read_fp)
                current_leaderboard = list(reader)
                fieldnames = reader.fieldnames
        except FileNotFoundError:
            with open(filename, newline='', mode='w') as create_fp:
                current_leaderboard = []
                fieldnames = ['BoardID', 'Player', 'Board', 'Time', 'MultiMode', 'Date']
        try:
            board_id = GameControl.compress_board_textually()
        except tk.TclError:
            return

        board_name = tk.StringVar(value='')
        player_name = tk.StringVar(value='')
        status = tk.StringVar(value='None')
        WindowControl.leaderboard_entry_window(
            player_name,
            board_name,
            status,
            (current_leaderboard, board_id)
        )

        if status.get().startswith('Failed:'):
            error_msg = status.get().split(':')[1]
            try:
                WindowControl.game_root.state()
                WindowControl.messagebox_open = True
                messagebox.showerror(title='FFM Leaderboard Error', message=f'Failed to save time to leaderboard.\n{error_msg}')
                WindowControl.messagebox_open = False
            except:
                pass
            return

        player_name = player_name.get()
        board_name = board_name.get()

        # Layout of CSV for storing records
        # ID, player name, board name, time, multimines, sq inc, mine inc, date
        new_entry = dict(zip(fieldnames, [
            board_id,
            player_name,
            board_name,
            f'{int(GameControl.seconds_elapsed)}',
            f'{int(Options.multimines)}',
            date.today().strftime('%m/%d/%y')
        ]))

        current_leaderboard.append(new_entry)
        with open(filename, 'w', newline='') as write_fp:
            writer = csv.DictWriter(write_fp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(current_leaderboard)


class BoardSquare(tk.Label):
    """A toggable square used in playing Minesweeper.

    Args:
        master (tk.Widget): Parent widget.
        size (int): Dimensions, in pixels.
        tk_image (tk.PhotoImage): Image displayed in square.

    Attributes:
        master (tk.Widget): Parent widget
        image (tk.PhotoImage): Image displayed in square.
        uncovered (bool): Flag for if the square has been uncovered.
        flagged (bool): Flag for if the square has been flagged.
        enabled (bool): Flag if the square is enabled to use in game.
        num_flags (int): Number of flags on the square.
        value (int): Number in the square.
        directions (tuple[str, str, str, str, str, str, str, str]): 8 main directions.
        neighbours (dict[str, BoardSquare]): Neighbouring squares, in each of the 8 directions.

    """
    def __init__(self, master, size, tk_image):
        super().__init__(master, height=size, width=size, im=tk_image, bd=0)
        self.master = master
        self.image = tk_image
        self.uncovered = False
        self.flagged = False
        self.enabled = True
        self.num_flags = 0
        self.value = 0
        self.directions = (tk.NW, tk.N, tk.NE, tk.W, tk.E, tk.SW, tk.S, tk.SE)
        self.neighbours = dict.fromkeys(self.directions)

    def link_to_neighbours(self):
        """Find and store all neighbouring squares."""
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

    def uncover(self):
        """Uncover the square if allowed and check if that results in thw game being won."""
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
                    GameControl.game_state = GameState.DONE
                    GameControl.new_game()
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

    def flag(self):  # For normal gameplay
        """Toggle a flag on the square, and update the counter."""
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

    def add_flag(self):  # For multimine
        """Add a flag to the square, and update the counter."""
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

    def remove_flag(self):  # For multimine
        """Remove a flag from the square, and update the counter."""
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

    def chord(self):
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

    def toggle_enable(self):
        """Toggle square between enabled and disabled."""
        if self.enabled:
            self.config(im=Constants.UNLOCKED_BLACK_SQUARE)
        else:
            self.config(im=self.image)
        self.enabled = not self.enabled

    def lock(self):
        """Lock the square so it can't be toggled."""
        if not self.enabled:
            self.config(im=Constants.LOCKED_BLACK_SQUARE)

    def unlock(self):
        """Unlock the square so it can be toggled."""
        if not self.enabled:
            self.config(im=Constants.UNLOCKED_BLACK_SQUARE)

    def reset(self):
        """Reset the square back to base initialization."""
        self.image = Constants.BOARD_IMAGES[20]
        self.config(im=self.image)
        self.uncovered = False
        self.flagged = False
        self.num_flags = 0
        self.enabled = True
        self.value = 0
        self.neighbours = dict.fromkeys(self.directions)


class WindowControl:
    """Utility class containing the window objects and related functions.

    Attributes:
        messagebox_open (bool): Flag if a messagebox is open so multiple are not created and stacked.
        hidden_root (tk.Tk): Absolute parent of the program. Only used for handling game close.
        game_root (tk.Toplevel): Main window of the program.
        main_frame (tk.Frame): Primary frame all other widgets reside in.
        menu_frame (tk.Frame): Frame all control widgets reside in.
        board_frame (tk.Frame): Frame all squares of the board reside in.
        mswpr_frame (tk.Frame): Frame to group various game widgets.
        presets_frame (tk.Frame): Frame to group preset widgets.
        diff_frame (tk.Frame): Frame to group difficulty widgets.
        timer_frame (tk.Frame): Frame to group timer widgets.
        flags_frame (tk.Frame): Frame to group flag widgets.
        controls_frame (tk.Frame): Frame to group control widgets.
        leaderboard_frame (tk.Frame): Frame to group leaderboard widgets.
        new_game_button (tk.Label): Game reset button.
        mode_switch_button (tk.Label): Click mode switch button.
        settings_button (tk.Button): Settings button.
        play_button (tk.Button): Play game button.
        stop_button (tk.Button): Stop game button.

    """
    messagebox_open = False

    hidden_root = tk.Tk()
    game_root = tk.Toplevel(class_='FreeForm Minesweeper')
    main_frame = tk.Frame(
        game_root, width=Options.window_width,
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
    leaderboard_frame = tk.Frame(menu_frame, bg=Constants.BACKGROUND_COLOUR)

    leaderboard_button = tk.Button(
        leaderboard_frame,
        width=Constants.BOARD_SQUARE_SIZE, height=Constants.BOARD_SQUARE_SIZE,
        bd=0, highlightthickness=0,
        bg=Constants.BACKGROUND_COLOUR, activebackground=Constants.BACKGROUND_COLOUR
    )
    new_game_button = tk.Label(
        mswpr_frame,
        width=Constants.BOARD_SQUARE_SIZE, height=Constants.BOARD_SQUARE_SIZE,
        bd=0, highlightthickness=0,
        bg=Constants.BACKGROUND_COLOUR, activebackground=Constants.BACKGROUND_COLOUR
    )
    mode_switch_button = tk.Label(
        mswpr_frame,
        width=Constants.BOARD_SQUARE_SIZE, height=Constants.BOARD_SQUARE_SIZE,
        bd=0, highlightthickness=0,
        bg=Constants.BACKGROUND_COLOUR, activebackground=Constants.BACKGROUND_COLOUR
    )
    settings_button = tk.Button(
        mswpr_frame,
        width=Constants.BOARD_SQUARE_SIZE, height=Constants.BOARD_SQUARE_SIZE,
        bd=0, highlightthickness=0,
        bg=Constants.BACKGROUND_COLOUR, activebackground=Constants.BACKGROUND_COLOUR
    )
    play_button = tk.Button(mswpr_frame, text='Play', width=5, command=GameControl.play_game)
    stop_button = tk.Button(mswpr_frame, text='Stop', width=5, command=GameControl.stop_game)

    @staticmethod
    def init_window():
        """Initialize window widgets."""
        WindowControl.hidden_root.withdraw()
        WindowControl.game_root.resizable(0, 0)
        WindowControl.game_root.title('FreeForm Minesweeper')
        WindowControl.game_root.protocol('WM_DELETE_WINDOW', WindowControl.hidden_root.destroy)
        WindowControl.game_root.bind('<Control-i>', lambda event: GameControl.invert_board())
        WindowControl.main_frame.grid_propagate(0)
        WindowControl.menu_frame.grid_propagate(0)
        WindowControl.board_frame.grid_propagate(0)
        for i in range(7):
            WindowControl.menu_frame.grid_columnconfigure(i, weight=1)
        WindowControl.menu_frame.grid(row=0, column=0, sticky=tk.NSEW)
        WindowControl.board_frame.grid(row=1, column=0, sticky=tk.NSEW)
        WindowControl.main_frame.grid(row=2, column=0, sticky=tk.NSEW)

    @staticmethod
    def init_board():
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
                sq.grid(row=x, column=y, sticky=tk.NSEW)

    @staticmethod
    def init_menu():
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
        preset_easy.grid(row=0, column=0, sticky=tk.NSEW)
        preset_medium.grid(row=0, column=1, sticky=tk.NSEW)
        preset_hard.grid(row=1, column=0, sticky=tk.NSEW)
        preset_expert.grid(row=1, column=1, sticky=tk.NSEW)
        WindowControl.presets_frame.grid(row=0, column=0)

        flag_left = tk.Label(WindowControl.flags_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        flag_mid = tk.Label(WindowControl.flags_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        flag_right = tk.Label(WindowControl.flags_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        flag_left.grid(row=0, column=0, sticky=tk.NSEW)
        flag_mid.grid(row=0, column=1, sticky=tk.NSEW)
        flag_right.grid(row=0, column=2, sticky=tk.NSEW)
        WindowControl.flags_frame.grid(row=0, column=1)

        WindowControl.play_button['font'] = Constants.FONT
        WindowControl.stop_button['font'] = Constants.FONT

        WindowControl.mode_switch_button.config(im=Constants.BOARD_IMAGES[17])
        WindowControl.new_game_button.config(im=Constants.BOARD_IMAGES[13])
        WindowControl.settings_button.config(im=Constants.BOARD_IMAGES[19], command=WindowControl.settings_window)
        WindowControl.mode_switch_button.grid(row=0, column=0, sticky=tk.NSEW)
        WindowControl.new_game_button.grid(row=0, column=1, padx=Constants.PADDING_DIST, pady=3, sticky=tk.NSEW)
        WindowControl.settings_button.grid(row=0, column=2, sticky=tk.NSEW)
        WindowControl.play_button.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)
        WindowControl.mswpr_frame.grid(row=0, column=2)

        timer_left = tk.Label(WindowControl.timer_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        timer_mid = tk.Label(WindowControl.timer_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        timer_right = tk.Label(WindowControl.timer_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        timer_left.grid(row=0, column=0, sticky=tk.NSEW)
        timer_mid.grid(row=0, column=1, sticky=tk.NSEW)
        timer_right.grid(row=0, column=2, sticky=tk.NSEW)
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
        diff_label.grid(row=0, column=1, columnspan=4, sticky=tk.NSEW)
        diff_1.grid(row=1, column=1, sticky=tk.NSEW)
        diff_2.grid(row=1, column=2, sticky=tk.NSEW)
        diff_3.grid(row=1, column=3, sticky=tk.NSEW)
        diff_4.grid(row=1, column=4, sticky=tk.NSEW)
        WindowControl.diff_frame.grid(row=0, column=4)

        fill_button = tk.Button(WindowControl.controls_frame, text='Fill', font=Constants.FONT, width=5, command=GameControl.fill_board)
        clear_button = tk.Button(WindowControl.controls_frame, text='Clear', font=Constants.FONT, width=5, command=GameControl.clear_board)
        save_board_button = tk.Button(WindowControl.controls_frame, text='Save', font=Constants.FONT, width=5, command=lambda: GameControl.save_board())
        load_board_button = tk.Button(WindowControl.controls_frame, text='Load', font=Constants.FONT, width=5, command=lambda: GameControl.load_board())

        WindowControl.leaderboard_button.config(im=Constants.LEADERBOARD_ICON_PNG, command=WindowControl.leaderboard_view_window)
        WindowControl.leaderboard_button.grid(row=0, column=0)
        WindowControl.leaderboard_frame.grid(row=0, column=5)

        fill_button.grid(row=0, column=1, sticky=tk.NSEW)
        clear_button.grid(row=1, column=1, sticky=tk.NSEW)
        save_board_button.grid(row=0, column=2, sticky=tk.NSEW)
        load_board_button.grid(row=1, column=2, sticky=tk.NSEW)
        WindowControl.controls_frame.grid(row=0, column=6)

    @staticmethod
    def init_dialogue_customization():
        """Customize existing dialogue boxes."""
        def __init__(self, title, prompt,
                    initialvalue=None,
                    minvalue = None, maxvalue = None,
                    parent = None, have_entry=True):
            self.prompt   = prompt
            self.minvalue = minvalue
            self.maxvalue = maxvalue
            self.initialvalue = initialvalue
            self.have_entry = have_entry
            simpledialog.Dialog.__init__(self, parent, title)

        def body(self, master):

            w = tk.Label(master, text=self.prompt, justify=tk.LEFT, font=Constants.FONT_BIG)
            w.grid(row=0, padx=5, sticky=tk.W)


            self.entry = tk.Entry(master, name='entry', font=Constants.FONT_BIG)
            if not self.have_entry:
                return w

            self.entry.grid(row=1, padx=5, sticky=tk.W+tk.E)
            if self.initialvalue is not None:
                self.entry.insert(0, self.initialvalue)
                self.entry.select_range(0, tk.END)

            return self.entry

        def buttonbox(self):
            box = tk.Frame(self)

            w = tk.Button(box, text='OK' if self.have_entry else 'Yes', width=5, command=self.ok, default=tk.ACTIVE, font=Constants.FONT)
            w.grid(column=0, row=0)
            w = tk.Button(box, text='Cancel' if self.have_entry else 'No', width=5, command=self.cancel, font=Constants.FONT)
            w.grid(column=1, row=0)

            self.bind('<Return>', self.ok)
            self.bind('<Escape>', self.cancel)

            box.pack()

        simpledialog._QueryDialog.__init__ = __init__
        simpledialog._QueryDialog.body = body
        simpledialog._QueryDialog.buttonbox = buttonbox
        simpledialog.ask = lambda title, prompt, **kw: simpledialog._QueryString(title, prompt, have_entry=False, **kw).result

    @staticmethod
    def update_timer():
        """Update timer widgets."""
        if (GameControl.squares_uncovered or GameControl.flags_placed) and GameControl.game_state is GameState.PLAYING and not GameControl.on_hold:
            seconds = list(str(int(GameControl.seconds_elapsed)).zfill(3))
            for number in WindowControl.timer_frame.grid_slaves():
                number.config(im=Constants.SEVSEG_IMAGES[int(seconds.pop())])

    @staticmethod
    def reset_timer():
        """Reset timer widgets."""
        for number in WindowControl.timer_frame.grid_slaves():
            number.config(im=Constants.SEVSEG_IMAGES[0])

    @staticmethod
    def update_flag_counter():
        """Update flag widgets."""
        flags = GameControl.num_mines - GameControl.flags_placed
        value_container = list(str(flags).zfill(3))
        for number in WindowControl.flags_frame.grid_slaves():
            number.config(im=Constants.SEVSEG_IMAGES[int(value_container.pop())])

    @staticmethod
    def reset_flag_counter():
        """Reset flag widgets."""
        for number in WindowControl.flags_frame.grid_slaves():
            number.config(im=Constants.SEVSEG_IMAGES[0])

    @staticmethod
    def drag_enable_toggle(event, initial_square):
        """Turn all squares under the mouse to a state based on an initial square while dragging.

        Args:
            event (tk.Event): Mouse motion event.
            initial_square (BoardSquare): The initial square the dragging began on.

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
    def lock_controls():
        """Lock the controls for the game."""
        WindowControl.settings_button.config(state=tk.DISABLED)
        WindowControl.play_button.config(state=tk.DISABLED)
        WindowControl.stop_button.config(state=tk.DISABLED)
        WindowControl.leaderboard_button.config(state=tk.DISABLED)
        WindowControl.new_game_button.unbind('<ButtonPress-1>')
        WindowControl.new_game_button.unbind('<ButtonRelease-1>')

    @staticmethod
    def unlock_controls():
        """Unlock the controls for the game."""
        WindowControl.settings_button.config(state=tk.NORMAL)
        WindowControl.play_button.config(state=tk.NORMAL)
        WindowControl.stop_button.config(state=tk.NORMAL)
        WindowControl.leaderboard_button.config(state=tk.NORMAL)
        WindowControl.new_game_button.bind('<ButtonPress-1>', lambda event: WindowControl.new_game_button.config(im=Constants.BOARD_IMAGES[14]))
        WindowControl.new_game_button.bind('<ButtonRelease-1>', lambda event: GameControl.new_game())

    @staticmethod
    def create_new_toplevel(title, class_, resizable, icon_ico, icon_png):
        """Create a new Toplevel/popup window with attributes.

        Args:
            title (str): Title of the window.
            class_ (str): WM Class of the window.
            resizable (tuple[int, int]): X and Y resizability of the window.
            icon_ico: ICO for window icon.
            icon_png: PNG for window icon.

        Returns:
            tk.Toplevel: Window created.
            function: Default function to be bound to the Toplevel's destruction. No parameters. Returns None.

        """
        WindowControl.lock_controls()
        toplevel_root = tk.Toplevel(class_=class_)
        toplevel_root.title(title)
        toplevel_root.resizable(*resizable)
        if MetaData.platform == 'Windows':
            toplevel_root.iconbitmap(icon_ico)
        elif MetaData.platform == 'Linux':
            toplevel_root.iconphoto(False, icon_png)

        def toplevel_root_close():
            try:
                WindowControl.unlock_controls()
            except tk.TclError:
                pass

        return (toplevel_root, toplevel_root_close)

    @staticmethod
    def settings_window():
        """Create and display the settings window."""
        settings_root, settings_root_close = WindowControl.create_new_toplevel(
            'FreeForm Minesweeper Options',
            'FFM Options',
            (0, 0),
            Constants.SETTINGS_ICON_ICO,
            Constants.SETTINGS_ICON_PNG
        )
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
        grace_label.pack(anchor=tk.W)
        grace_on_choice.pack(anchor=tk.W)
        grace_off_choice.pack(anchor=tk.W)
        grace_frame.grid(row=1, column=0, sticky=tk.W, pady=Constants.PADDING_DIST)

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
        multi_label.pack(anchor=tk.W)
        normal_choice.pack(anchor=tk.W)
        multi_choice.pack(anchor=tk.W)
        multi_frame.grid(row=2, column=0, sticky=tk.W, pady=Constants.PADDING_DIST)

        mines = tk.DoubleVar(settings_root, Options.multimine_mine_inc)
        mines_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        mines_label = tk.Label(mines_frame, text='MultiMine Mine Increase', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        mines_slider = tk.Scale(
            mines_frame, variable=mines, orient=tk.HORIZONTAL, font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR,
            resolution=0.01, from_=0.0, to=0.6, length=300, bd=0
        )
        mines_label.pack(anchor=tk.W)
        mines_slider.pack()
        mines_frame.grid(row=3, column=0, sticky=tk.W, pady=Constants.PADDING_DIST)

        density = tk.DoubleVar(settings_root, Options.multimine_sq_inc)
        density_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        density_label = tk.Label(density_frame, text='MultiMine Probability', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        density_slider = tk.Scale(
            density_frame, variable=density, orient=tk.HORIZONTAL, font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR,
            resolution=0.01, from_=0.1, to=0.9, length=300, bd=0
        )
        density_label.pack(anchor=tk.W)
        density_slider.pack()
        density_frame.grid(row=4, column=0, sticky=tk.W, pady=Constants.PADDING_DIST)

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
        flagless_label.pack(anchor=tk.W)
        flagless_off_choice.pack(anchor=tk.W)
        flagless_on_choice.pack(anchor=tk.W)
        flagless_frame.grid(row=5, column=0, sticky=tk.W, pady=Constants.PADDING_DIST)

        rows = tk.IntVar(settings_root, Options.rows)
        rows_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        rows_label = tk.Label(rows_frame, text='Rows', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        rows_slider = tk.Scale(
            rows_frame, variable=rows, orient=tk.HORIZONTAL, font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR,
            resolution=1, from_=Constants.MIN_ROWS, to=Constants.MAX_ROWS, length=300, bd=0
        )
        rows_label.pack(anchor=tk.W)
        rows_slider.pack()
        rows_frame.grid(row=6, column=0, sticky=tk.W, pady=Constants.PADDING_DIST)

        columns = tk.IntVar(settings_root, Options.cols)
        columns_frame = tk.Frame(settings_root, bg=Constants.DEFAULT_COLOUR)
        columns_label = tk.Label(rows_frame, text='Columns', font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR)
        columns_slider = tk.Scale(
            rows_frame, variable=columns, orient=tk.HORIZONTAL, font=Constants.FONT_BIG, bg=Constants.DEFAULT_COLOUR,
            resolution=1, from_=Constants.MIN_COLUMNS, to=Constants.MAX_COLUMNS, length=300, bd=0
        )
        columns_label.pack(anchor=tk.W)
        columns_slider.pack()
        columns_frame.grid(row=6, column=0, sticky=tk.W, pady=Constants.PADDING_DIST)

        def submit_vars():
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
            WindowControl.settings_button.config(state=tk.NORMAL)
            WindowControl.play_button.config(state=tk.NORMAL)

        submit_button = tk.Button(settings_root, text='Apply Settings', font=Constants.FONT, command=submit_vars)
        submit_button.grid(row=7, column=0, pady=Constants.PADDING_DIST)

    @staticmethod
    def leaderboard_entry_window(player_var, board_var, status_flag, leaderboard_info):
        """Create and display the leaderboard entry window to accept new times.

        Args:
            player_var (tk.StringVar): String variable tracking the name of the player.
            board_var (tk.StringVar): String variable tracking the name of the board the player provides.
            status_flag (tk.StringVar): String variable tracking the status of submitting a leaderboard entry.
            leaderboard_info (tuple): Tuple containing the current leaderboard and the ID of the current board.

        """
        leaderboard, board_id = leaderboard_info
        boards_with_id = [board for board in leaderboard if board['BoardID'] == board_id]
        submitting = False

        def save_time_root_close():
            """Handler for leaderboard entry window closing."""
            try:
                WindowControl.lock_controls()
            except Exception:
                status_flag.set('Failed:Main window destroyed')
            else:
                if status_flag.get() != 'Success':
                    status_flag.set('Failed:Window closed without saving')

        def submit_name_player():
            """Validate user inputted names and close window if they satisfy requirements."""
            nonlocal submitting
            submitting = True
            board_var.set(board_var.get().upper())
            player_var.set(player_var.get().upper())
            submitting = False
            if not board_var.get() or not player_var.get():
                status_flag.set('Failed:Names entered cannot be blank')
                return
            if not (board_var.get().isalpha() and player_var.get().isalpha()):
                status_flag.set('Failed:Names entered can only contain letters [A-Z]')
                return
            for entry in leaderboard:
                if entry['Player'] == player_var.get() and entry['Board'] == board_var.get():
                    status_flag.set('Failed:Board names must be unique for a player')
                    return
            status_flag.set('Success')
            save_time_root.destroy()

        def autofill_board_name():
            """Autofill the name in the board entry based on the current board and player."""
            board_for_player = [
                board['Board']
                for board in boards_with_id
                if board['Player'] == player_var.get().upper() and
                int(board['MultiMode']) == Options.multimines
            ]
            if board_for_player:
                board_var.set(board_for_player[0])
                name_entry.config(state=tk.DISABLED)
            elif not submitting:
                name_entry.config(state=tk.NORMAL)
                name_entry.delete(0, tk.END)

        player_var.trace_add('write', lambda *_: autofill_board_name())

        save_time_root, _ = WindowControl.create_new_toplevel(
            'Save to Leaderboard',
            'FFM Leaderboard',
            (0, 0),
            Constants.LEADERBOARD_ICON_ICO,
            Constants.LEADERBOARD_ICON_PNG
        )
        save_time_root.bind('<Destroy>', lambda event: save_time_root_close())

        save_time_frame = tk.Frame(save_time_root, bg=Constants.BACKGROUND_COLOUR, width=400, height=200 if not Options.multimines else 250)
        save_time_frame.grid_propagate(False)
        save_time_frame.grid_columnconfigure(0, weight=1)
        save_time_frame.grid_rowconfigure(8, weight=1)

        time_label = tk.Label(save_time_frame, text=f'Your time was: {int(GameControl.seconds_elapsed)} seconds.', font=Constants.FONT_BIG, bg=Constants.BACKGROUND_COLOUR)
        player_label = tk.Label(save_time_frame, text='Player Name', font=Constants.FONT_BIG, bg=Constants.BACKGROUND_COLOUR)
        player_entry = tk.Entry(save_time_frame, exportselection=False, font=Constants.FONT_BIG, textvariable=player_var)
        name_label = tk.Label(save_time_frame, text='Name This Board', font=Constants.FONT_BIG, bg=Constants.BACKGROUND_COLOUR)
        name_entry = tk.Entry(save_time_frame, exportselection=False, font=Constants.FONT_BIG, textvariable=board_var)
        save_button = tk.Button(save_time_frame, text='Save Time', font=Constants.FONT_BIG, command=submit_name_player)

        if Options.multimines:
            multimine_label = tk.Label(save_time_frame, text='You played on multimine mode', font=Constants.FONT_BIG, bg=Constants.BACKGROUND_COLOUR)
            multimine_label.grid(row=5, column=0, pady=6)

        time_label.grid(row=0, column=0, pady=6)
        player_label.grid(row=1, column=0)
        player_entry.grid(row=2, column=0)
        name_label.grid(row=3, column=0)
        name_entry.grid(row=4, column=0)
        save_button.grid(row=8, column=0)
        save_time_frame.grid(row=0, column=0)

        player_entry.focus()
        player_entry.bind('<Control-KeyRelease-a>', lambda event: player_entry.select_range(0, tk.END))
        name_entry.bind('<Control-KeyRelease-a>', lambda event: name_entry.select_range(0, tk.END))
        save_time_root.bind('<Return>', lambda event: submit_name_player())
        save_button.wait_variable(status_flag)

    @staticmethod
    def leaderboard_view_window(leaderboard_file=Constants.LEADERBOARD_FILENAME):
        """Create and display window to view leaderboard in.

         Args:
            leaderboard_info (str, optional): The current leaderboard file path.
                                              Defaults to Constants.LEADERBOARD_FILENAME.

        """
        MAX_WIDTH = 400
        NOTEBOOK_HEIGHT = 132 + Constants.FONT_BIG.metrics('linespace')
        player_var = tk.StringVar()
        notebook_pages = []
        selected_page_index = 0
        canvas_right_clicked = None
        canvas_right_clicked_time_id = None

        with open(leaderboard_file, 'r', newline='') as fp:
            reader = csv.DictReader(fp)
            current_leaderboard = list(reader)
            fieldnames = reader.fieldnames

        def update_leaderboard():
            """Write the current local leaderboard to disk."""
            with open(leaderboard_file, 'w', newline='') as write_fp:
                writer = csv.DictWriter(write_fp, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(current_leaderboard)

        def rename_player():
            """Rename a player in the leaderboard."""
            new_player_name = simpledialog.askstring(
                'FFMS Player Name Change',
                'Enter New Name [A-Z]',
                parent=leaderboard_view_root
            )
            if new_player_name is None:
                return
            if not new_player_name.isalpha():
                WindowControl.messagebox_open = True
                messagebox.showerror(title='FFM Leaderboard Error', message='Names entered can only contain letters [A-Z]')
                WindowControl.messagebox_open = False
                return
            new_player_name = new_player_name.upper()
            if new_player_name:
                old_player_name = player_var.get().upper()
                for entry in current_leaderboard:
                    if entry['Player'] == new_player_name:
                        WindowControl.messagebox_open = True
                        messagebox.showerror(title='FFM Leaderboard Error', message='Player names already exists')
                        WindowControl.messagebox_open = False
                        return
                for entry in current_leaderboard:
                    if entry['Player'] == old_player_name:
                        break
                else:
                    WindowControl.messagebox_open = True
                    messagebox.showerror(title='FFM Leaderboard Error', message='Player cannot be renamed.\nPlayer does not exist')
                    WindowControl.messagebox_open = False
                    return
                for entry in current_leaderboard:
                    if entry['Player'] == old_player_name:
                        entry['Player'] = new_player_name
                player_var.set(new_player_name)
                update_leaderboard()

        def rename_board():
            """Rename a board in the leaderboard."""
            new_board_name = simpledialog.askstring(
                'FFMS Board Name Change',
                'Enter New Name [A-Z]',
                parent=leaderboard_view_root
            )
            if new_board_name is None:
                return
            if not new_board_name.isalpha():
                WindowControl.messagebox_open = True
                messagebox.showerror(title='FFM Leaderboard Error', message='Names entered can only contain letters [A-Z]')
                WindowControl.messagebox_open = False
                return
            new_board_name = new_board_name.upper()
            if new_board_name:
                nb = notebook_pages[selected_page_index]
                old_board_name = nb.tab(nb.select(), 'text').upper()
                player = player_var.get().upper()
                for entry in current_leaderboard:
                    if entry['Player'] == player and entry['Board'] == new_board_name and entry['Board'] != old_board_name:
                        WindowControl.messagebox_open = True
                        messagebox.showerror(title='FFM Leaderboard Error', message='Board names must be unique for a player')
                        WindowControl.messagebox_open = False
                        return
                for entry in current_leaderboard:
                    if entry['Board'] == old_board_name and entry['Player'] == player:
                        entry['Board'] = new_board_name
                display_boards_from_player()
                update_leaderboard()

        def delete_board():
            """Delete all a boards times from a player."""
            nonlocal current_leaderboard, selected_page_index
            sure = simpledialog.ask(
                'FFMS Leaderboard Deletion',
                'Are you sure you wish to delete\n all of this board\'s entries?',
                parent=leaderboard_view_root
            )
            if sure is None:
                return
            nb = notebook_pages[selected_page_index]
            tab_text = nb.tab(nb.select(), 'text').upper()
            current_leaderboard = [
                entry for entry in current_leaderboard
                if entry['Player'] != player_var.get().upper() or entry['Board'] != tab_text
            ]
            selected_page_index = 0
            display_boards_from_player()
            update_leaderboard()

        def delete_time():
            """Delete a single time from a player."""
            sure = simpledialog.ask(
                'FFMS Leaderboard Deletion',
                'Are you sure you wish to delete this entry?',
                parent=leaderboard_view_root
            )
            if sure is None:
                return
            nb = notebook_pages[selected_page_index]
            selected_entry_text = canvas_right_clicked.itemcget(canvas_right_clicked_time_id, 'text').split()
            time = int(selected_entry_text[0])
            date = selected_entry_text[-1]
            board = nb.tab(nb.select(), 'text').upper()
            player = player_var.get().upper()
            entry_to_remove = None
            for entry in current_leaderboard:
                if entry['Player'] == player and entry['Board'] == board and entry['Date'] == date and int(entry['Time']) == time:
                    entry_to_remove = entry
                    break
            current_leaderboard.remove(entry_to_remove)
            display_boards_from_player()
            update_leaderboard()

        def canvas_item_popup(event, canvas, popup):
            """Create a popup menu on a canvas in response to an event.

            Args:
                event (tk.Event): Event causing the popup to occur.
                canvas (tk.Canvas): Canvas receiving the event.
                popup (tk.Menu): Menu to display as a popup.

            """
            nonlocal canvas_right_clicked, canvas_right_clicked_time_id
            try:
                canvas_item_id = event.widget.find_withtag('current')[0]
            except IndexError:
                return
            canvas_right_clicked = canvas
            canvas_right_clicked_time_id = canvas_item_id
            WindowControl.make_popup_menu(event, popup)

        def display_boards_from_player():
            """Display the boards from a player in a paginated notebook."""
            nonlocal selected_page_index
            boards = [entry for entry in current_leaderboard if entry['Player'] == player_var.get().upper()]
            page_left_btn.grid_remove()
            page_right_btn.grid_remove()
            if not boards and notebook_pages and isinstance(notebook_pages[0], tk.Label):
                return
            for page in notebook_pages:
                page.destroy()

            current_width = 0
            selected_page_index = 0
            current_notebook_page = ttk.Notebook(leaderboard_view_frame, width=MAX_WIDTH, height=NOTEBOOK_HEIGHT)
            notebook_pages.clear()

            ids_covered = {}
            for board in boards:
                current_board_id = board['BoardID']
                current_multimode = board['MultiMode']
                if current_board_id in ids_covered and ids_covered[current_board_id] == current_multimode:
                    continue
                tab_text = board['Board']
                current_width += max(Constants.FONT_BIG.measure(tab_text) + 8, 23)
                if current_width >= MAX_WIDTH:
                    notebook_pages.append(current_notebook_page)
                    current_notebook_page = ttk.Notebook(leaderboard_view_frame, width=MAX_WIDTH, height=NOTEBOOK_HEIGHT)
                    current_width = 0

                entry_frame = tk.Frame(current_notebook_page, height=NOTEBOOK_HEIGHT, width=MAX_WIDTH)
                thumbnail_tk = ImageTk.PhotoImage(image=WindowControl.generate_board_thumbnail(current_board_id))
                entry_thumbnail_label = tk.Label(entry_frame, height=128, width=128, im=thumbnail_tk)
                entry_thumbnail_label.image = thumbnail_tk

                multimode_label = tk.Label(entry_frame, font=Constants.FONT_BIG, text='Normal Mode')
                if current_multimode == '1':
                    multimode_label.config(text='MultiMine Mode')
                times_canvas = tk.Canvas(entry_frame, width=MAX_WIDTH - 128 - 20, height=128)
                times_scrollbar = tk.Scrollbar(entry_frame, orient=tk.VERTICAL, width=16, command=times_canvas.yview)

                times = [
                    board for board in boards
                    if board['BoardID'] == current_board_id and
                    board['MultiMode'] == current_multimode
                ]

                TEXT_HEIGHT = Constants.FONT_BIG.cget('size') + 10
                for i, time in enumerate(sorted(times, key=lambda time: int(time['Time']))):
                    time_text = f'{time["Time"]:0>3} seconds  {time["Date"]}'
                    times_canvas.create_text(
                        0, TEXT_HEIGHT * i,
                        text=time_text, font=Constants.FONT_BIG,
                        tags='entry_text',
                        activefill='#444444'
                    )

                times_canvas.config(yscrollcommand=times_scrollbar.set, scrollregion=times_canvas.bbox(tk.ALL))
                if TEXT_HEIGHT * len(times) > NOTEBOOK_HEIGHT:
                    times_scrollbar.grid(row=1, column=2, sticky=tk.N+tk.S)
                    times_canvas.yview_moveto('0.0')

                multimode_label.grid(row=0, column=1)
                times_canvas.grid(row=1, column=1)
                entry_thumbnail_label.grid(row=0, column=0, rowspan=2, sticky=tk.N)
                current_notebook_page.add(entry_frame, text=tab_text)
                ids_covered[current_board_id] = current_multimode
                current_notebook_page.bind(
                    '<Button-3>',
                    lambda event, current_notebook_page=current_notebook_page: WindowControl.menu_on_notebook_tab_click(event, current_notebook_page, notebook_popup_menu)
                )
                times_canvas.bind('<Button-3>', lambda event, canvas=times_canvas: canvas_item_popup(event, canvas, time_popup_menu))

            if boards:
                notebook_pages.append(current_notebook_page)
            if notebook_pages:
                page_left_btn.grid(row=3, column=0, sticky=tk.E)
                page_right_btn.grid(row=3, column=1, sticky=tk.W)
                for page in notebook_pages:
                    page.enable_traversal()
            else:
                notebook_pages.append(tk.Label(leaderboard_view_root, text='No boards for this player', font=Constants.FONT_BIG))
            notebook_pages[0].grid(row=2, column=0, columnspan=2, pady=(10, 0))
            change_notebook_page(0)

        def change_notebook_page(step):
            """Change the displayed notebook in a paginated list of notebooks.

            Args:
                step (int): Amount of pages to move. Negative numbers move left and positive numbers move right.

            """
            nonlocal selected_page_index
            if (selected_page_index + step) in range(len(notebook_pages)):
                notebook_pages[selected_page_index].grid_remove()
                selected_page_index += step
                notebook_pages[selected_page_index].grid(row=2, column=0, columnspan=2, pady=(10, 0))
            if selected_page_index == 0:
                page_left_btn.config(state=tk.DISABLED)
            else:
                page_left_btn.config(state=tk.NORMAL)
            if selected_page_index == len(notebook_pages) - 1:
                page_right_btn.config(state=tk.DISABLED)
            else:
                page_right_btn.config(state=tk.NORMAL)

        leaderboard_view_root, leaderboard_view_root_close = WindowControl.create_new_toplevel(
            'FreeForm Minesweeper Leaderboard',
            'FFM Leaderboard',
            (0, 0),
            Constants.LEADERBOARD_ICON_ICO,
            Constants.LEADERBOARD_ICON_PNG
        )
        leaderboard_view_root.bind('<Destroy>', lambda event: leaderboard_view_root_close())

        leaderboard_view_frame = tk.Frame(leaderboard_view_root, width=MAX_WIDTH)
        page_left_btn = tk.Button(
            leaderboard_view_frame, height=1,
            text='<<', font=Constants.FONT,
            command=lambda: change_notebook_page(-1)
        )
        page_right_btn = tk.Button(
            leaderboard_view_frame, height=1,
            text='>>', font=Constants.FONT,
            command=lambda: change_notebook_page(1)
        )

        notebook_popup_menu = tk.Menu(leaderboard_view_root, tearoff=0)
        notebook_popup_menu.add_command(label='Rename', command=lambda: rename_board())
        notebook_popup_menu.add_command(label='Delete', command=lambda: delete_board())
        notebook_popup_menu.add_separator()
        notebook_popup_menu.add_command(label='Close')

        time_popup_menu = tk.Menu(leaderboard_view_root, tearoff=0)
        time_popup_menu.add_command(label='Delete', command=lambda: delete_time())
        time_popup_menu.add_separator()
        time_popup_menu.add_command(label='Close')

        player_entry_popup_menu = tk.Menu(leaderboard_view_root, tearoff=0)
        player_entry_popup_menu.add_command(label='Rename', command=lambda: rename_player())
        player_entry_popup_menu.add_separator()
        player_entry_popup_menu.add_command(label='Close')

        player_label = tk.Label(leaderboard_view_frame, text='Player Name', font=Constants.FONT_BIG)
        player_entry = tk.Entry(leaderboard_view_frame, exportselection=False, font=Constants.FONT_BIG, textvariable=player_var, width=20)

        s = ttk.Style()
        s.configure('TNotebook.Tab', font=Constants.FONT_BIG, padding=[0,0])
        s.configure('TNotebook', tabmargins=[2,2,2,2])
        display_boards_from_player()
        change_notebook_page(0)
        total_height = sum(widget.winfo_reqheight() for widget in leaderboard_view_frame.winfo_children())
        leaderboard_view_root.minsize(width=MAX_WIDTH + 2, height=total_height)
        player_label.grid(row=0, column=0, columnspan=2)
        player_entry.grid(row=1, column=0, columnspan=2, padx=(MAX_WIDTH + 2 - player_entry.winfo_reqwidth())//2)
        leaderboard_view_frame.grid(row=0, column=0, columnspan=2)
        player_entry.focus_set()
        player_entry.bind('<Control-KeyRelease-a>', lambda event: player_entry.select_range(0, tk.END))
        player_entry.bind('<Button-3>', lambda event: WindowControl.make_popup_menu(event, player_entry_popup_menu))
        player_var.trace_add('write', lambda *_: display_boards_from_player())
        player_var.trace_add('write', lambda *_: player_var.set(player_var.get().upper()) if not player_var.get().isupper() else None)

    @staticmethod
    def generate_board_thumbnail(compressed_board_id):
        """Generate a black and white image respresenting a board.

        Args:
            compressed_board_id (list[str]): List of binary strings representing the board.
                                             Active squares are displayed as white, and inactive as black.

        Returns:
            PIL.Image: Image generated from board.

        """
        board_bits = GameControl.decompress_board_textually(compressed_board_id)
        max_dim_y = len(max(board_bits, key=len))
        max_dim_x = len(board_bits)
        overall_max_dim = max(max_dim_y, max_dim_x)
        if overall_max_dim <= 16:
            size = 16
        elif overall_max_dim <= 32:
            size = 32
        else:
            size = 64
        padding_y = (size - max_dim_y) // 2
        padding_x = (size - max_dim_x) // 2
        thumbnail = Image.new(mode='RGBA', size=(size, size), color=(0, 0, 0))
        for x, bit_row in enumerate(board_bits):
            for y, bit in enumerate(bit_row):
                if int(bit):
                    thumbnail.putpixel((y + padding_y, x + padding_x), (255, 255, 255))
        thumbnail = thumbnail.resize((128, 128), resample=Image.NEAREST)
        return thumbnail

    @staticmethod
    def make_popup_menu(event, menu):
        """Display a popup menu on the screen at the position of the mouse.

        Args:
            event (tk.Event): The event causing the menu to occur. Intended to be a (right) mouse click.
            menu (tk.Menu): Menu to display on the screen.

        """
        try:
            root = event.widget.winfo_toplevel()
            is_over_menu = tk.BooleanVar(master=root, value=True)
            def close_on_click():
                if not is_over_menu.get():
                    menu.unpost()
                    root.unbind('<Button>', bind_id_button)
                    root.unbind('<FocusOut>', bind_id_focus)
            menu.post(event.x_root, event.y_root)
            menu.bind('<Enter>', lambda event: is_over_menu.set(True))
            menu.bind('<Leave>', lambda event: is_over_menu.set(False))
            bind_id_button = root.bind('<Button>', lambda event:close_on_click(), '+')
            bind_id_focus = root.bind('<FocusOut>', lambda event:close_on_click(), '+')
        finally:
            menu.grab_release()

    @staticmethod
    def menu_on_notebook_tab_click(event, notebook, menu):
        """Display a popup menu when the active tab of a notebook is clicked.

        Args:
            event (tk.Event): Event triggering the popup to occur.
            notebook (ttk.Notebook): The notebook receiving the event.
            menu (tk.Menu): The popup menu to display.
        """
        clicked_tab = notebook.tk.call(notebook._w, 'identify', 'tab', event.x, event.y)
        active_tab = notebook.index(notebook.select())
        if clicked_tab == active_tab:
            WindowControl.make_popup_menu(event, menu)


def main():
    """Initialize all game components and run the mainloop."""
    WindowControl.init_window()
    Constants.init_fonts()
    Constants.init_board_images()
    Constants.init_sevseg_images()
    Constants.init_extended_board_images()
    Constants.init_window_icons()
    WindowControl.init_dialogue_customization()
    Constants.DEFAULT_COLOUR = WindowControl.game_root.cget('bg')
    if MetaData.platform == 'Windows':
        WindowControl.game_root.iconbitmap(Constants.MAIN_ICON_ICO)
    elif MetaData.platform == 'Linux':
        WindowControl.game_root.iconphoto(False, Constants.MAIN_ICON_PNG)
    WindowControl.init_menu()
    WindowControl.diff_frame.grid_slaves()[-2].invoke()
    WindowControl.init_board()
    if not MetaData.is_release_up_to_date():
        MetaData.outdated_notice()
    tkFont.Font(name='TkCaptionFont', exists=True).config(family=Constants.FONT.cget('family'), size=Constants.FONT_BIG.cget('size'))
    # WindowControl.game_root.bind('y', lambda event: GameControl.save_time_to_file())
    while True:
        try:
            WindowControl.game_root.update_idletasks()
            WindowControl.game_root.update()
        except tk.TclError:
            break
        else:
            time.sleep(Constants.MAINLOOP_TIME)
            if (GameControl.squares_uncovered or GameControl.flags_placed) and GameControl.game_state is GameState.PLAYING:
                GameControl.seconds_elapsed = min(round(GameControl.seconds_elapsed + Constants.MAINLOOP_TIME, 2), 999)
                if int(GameControl.seconds_elapsed) == GameControl.seconds_elapsed:
                    WindowControl.update_timer()


if __name__ == '__main__':
    main()
