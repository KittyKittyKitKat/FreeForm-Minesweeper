# Copyright © Simon Harris-Palmer 2023. All rights reserved.

"""The game FreeForm Minesweeper, bundled with MultiMinesweeper mode.

Play the game by executing the file with Python >= 3.11 as a program, and have fun!
"""

import tkinter as tk
import tkinter.ttk as ttk
from enum import StrEnum, auto
from functools import cached_property
from itertools import chain, groupby
from math import ceil
from pathlib import Path, PurePath
from random import sample
from time import sleep
from tkinter import filedialog
from typing import Final

from boardsquare import BoardSquare
from dialogues import (
    AcknowledgementDialogue,
    AcknowledgementWithLinkDialogue,
    LeaderboardEntryDialogue,
    LeaderboardViewDialogue,
    SettingsDialogue,
    YesNoDialogue,
)
from imagehandler import ImageHandler
from releasemanager import ReleaseManager


# Potential rework of dark mode square graphics
class FreeFormMinesweeper:
    """A game of FreeForm Minesweeper."""

    class State(StrEnum):
        """Enum representing the current state of the game."""

        DRAW = auto()
        SWEEP = auto()
        PAUSE = auto()

    class ClickMode(StrEnum):
        """Enum representing the current clicking mode of the game."""

        UNCOVER = auto()
        FLAG = auto()
        FLAGLESS = auto()

    def __init__(self) -> None:
        """Initialize a game of FreeForm Minesweeper."""
        # Constants
        self.MAINLOOP_TIME: Final = 0.01
        self.UI_PADDING: Final = 4
        self.LIGHT_BACKGROUND_COLOUR: Final = '#c0c0c0'
        self.DARK_BACKGROUND_COLOUR: Final = '#3f3f3f'
        self.LIGHT_UI_COLOUR: Final = '#d9d9d9'
        self.DARK_UI_COLOUR: Final = '#666666'
        self.LIGHT_TEXT_COLOUR: Final = '#000000'
        self.DARK_TEXT_COLOUR: Final = '#ffffff'
        self.FILE_EXTENSION: Final = '.ffmnswpr'
        self.FILE_TYPE: Final = (
            ('FreeForm Minesweeper Board', f'*{self.FILE_EXTENSION}'),
        )
        Path('README.txt').write_text(Path('README.md').read_text())
        self.TUTORIAL_PAGE: Final = Path('tutorial.html').absolute().as_uri()
        self.GITHUB_PAGE: Final = 'https://github.com/KittyKittyKitKat/'
        self.SAVE_LOAD_DIR: Final = str(Path.home())
        self.SMALL_SCALE: Final = 'small'
        self.LARGE_SCALE: Final = 'large'
        self.SMALL_FONT: Final = ('Courier', 8, 'bold')
        self.LARGE_FONT: Final = ('Courier', 10, 'bold')
        self.DIFF_EASY: Final = 0.13
        self.DIFF_MEDIUM: Final = 0.16
        self.DIFF_HARD: Final = 0.207
        self.DIFF_EXPERT: Final = 0.25

        # Instance level UI elements
        self._hidden_root = tk.Tk()
        self.game_root = tk.Toplevel(class_='FreeForm Minesweeper')
        self.ih = ImageHandler()
        self.style = ttk.Style()
        self.menubar = tk.Menu(self.game_root)

        self.main_frame = ttk.Frame(self.game_root)
        self.menu_frame = ttk.Frame(self.main_frame)
        self.board_frame = ttk.Frame(self.main_frame)

        self.presets_frame = ttk.Frame(self.menu_frame)
        self.flags_frame = ttk.Frame(self.menu_frame)
        self.mswpr_frame = ttk.Frame(self.menu_frame)
        self.timer_frame = ttk.Frame(self.menu_frame)
        self.diff_frame = ttk.Frame(self.menu_frame)
        self.controls_frame = ttk.Frame(self.menu_frame)

        self.mode_switch_button = ttk.Label(self.mswpr_frame)
        self.new_game_button = ttk.Label(self.mswpr_frame)
        self.leaderboard_button = ttk.Button(self.mswpr_frame)
        self.play_button = ttk.Button(self.mswpr_frame)
        self.stop_button = ttk.Button(self.mswpr_frame)

        # Options
        self.rows = tk.IntVar(value=28)
        self.rows.trace_add('write', lambda *_: self.rows_trace())

        self.columns = tk.IntVar(value=30)
        self.columns.trace_add('write', lambda *_: self.columns_trace())

        self.board_scale = tk.StringVar(value=self.LARGE_SCALE)
        self.board_scale.trace_add('write', lambda *_: self.board_scale_trace())

        self.ui_scale = tk.StringVar(value=self.LARGE_SCALE)
        self.ui_scale.trace_add('write', lambda *_: self.ui_scale_trace())

        self.theme_option = tk.StringVar(value=self.ih.ImageTheme.LIGHT.value)
        self.theme_option.trace_add('write', lambda *_: self.theme_option_trace())

        self.multimine = tk.BooleanVar(value=False)
        self.multimine.trace_add('write', lambda *_: self.multimine_trace())

        self.multimine_diff_inc = tk.DoubleVar(value=0.25)

        self.multimine_likelihood = tk.DoubleVar(value=0.5)

        self.mine_spread = tk.DoubleVar(value=1.01)

        self.flagless = tk.BooleanVar(value=False)
        self.flagless.trace_add('write', lambda *_: self.flagless_trace())

        self.grace_rule = tk.BooleanVar(value=True)

        self.adaptive_ui = tk.BooleanVar(value=True)
        self.adaptive_ui.trace_add('write', lambda *_: self.adaptive_ui_trace())

        self.mode_key_behaviour = tk.StringVar(value='hold')
        self.mode_key_behaviour.trace_add(
            'write',
            lambda *_: self.mode_key_behaviour_trace(),
        )

        self.prompt_leaderboard_save = tk.BooleanVar(value=True)

        self.classic_ui = tk.BooleanVar(value=False)
        self.classic_ui.trace_add('write', lambda *_: self.classic_ui_trace())

        # Values related to setting the options
        self.theme: ImageHandler.ImageTheme = self.ih.ImageTheme.LIGHT
        self.background_colour = self.LIGHT_BACKGROUND_COLOUR
        self.ui_colour = self.LIGHT_UI_COLOUR
        self.text_colour = self.LIGHT_TEXT_COLOUR
        self.board_square_size: ImageHandler.ImageSize = self.ih.ImageSize.LG_SQUARE
        self.ui_square_size: ImageHandler.ImageSize = self.ih.ImageSize.LG_SQUARE
        self.sevseg_size: ImageHandler.ImageSize = self.ih.ImageSize.LG_SEVSEG
        self.max_flags = 1
        self.board_square_size_px = int(self.board_square_size.value.split('x')[0])
        self.mode_key_down = False
        self.ignore_toggle_key_held = True

        # Game instance variables
        self.difficulty = tk.DoubleVar(value=self.DIFF_EASY)
        self.state = self.State.DRAW
        self.click_mode = tk.StringVar(value=self.ClickMode.UNCOVER)
        self.click_mode.trace_add('write', lambda *_: self.click_mode_trace())
        self.draw_history: list[list[BoardSquare]] = []
        self.draw_history_buffer: list[list[BoardSquare]] = []
        self.draw_history_step: list[BoardSquare] = []
        self.num_mines = 0
        self.squares_cleared = 0
        self.flags_placed = 0
        self.squares_to_win = 0
        self.time_elapsed = 0.0
        self.currently_held_square = None

        # Set up all UI elements, split into methods for readability
        self.init_style()
        self.init_window()
        self.init_toolbar()
        self.init_menu()
        self.game_root.update()
        self.init_board()
        self.init_keybinds()
        self.game_root.title('FreeForm Minesweeper')
        self.alive = True

        # Release Manager
        self.rm = ReleaseManager(self.game_root)
        if not self.rm.is_release_up_to_date():
            self.rm.outdated_notice()

    # Traces and other Setting/Options Functions

    def rows_trace(self) -> None:
        """Update the number of rows in the board."""
        self.set_guard()

        rows = self.rows.get()
        num_rows_present = 0
        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            row = square.position[0]
            num_rows_present = max(num_rows_present, row)
        self.board_frame.config(height=self.board_square_size_px * rows)
        self.game_root.update_idletasks()
        self.game_root.update()
        if num_rows_present < rows - 1:
            for x in range(num_rows_present + 1, rows):
                for y in range(self.columns.get()):
                    self.make_square(x, y)
        elif num_rows_present > rows - 1:
            for i in range(num_rows_present, rows - 1, -1):
                for widget in self.board_frame.grid_slaves(row=i):
                    widget.grid_forget()
                    widget.destroy()

        self.unset_guard()

    def columns_trace(self) -> None:
        """Update the number of columns in the board."""
        self.set_guard()

        columns = self.columns.get()
        num_columns_present = 0
        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            column = square.position[1]
            num_columns_present = max(num_columns_present, column)
        self.board_frame.config(width=self.board_square_size_px * columns)
        self.game_root.update_idletasks()
        self.game_root.update()
        if num_columns_present < columns - 1:
            for y in range(num_columns_present + 1, columns):
                for x in range(self.rows.get()):
                    self.make_square(x, y)
        elif num_columns_present > columns - 1:
            for i in range(num_columns_present, columns - 1, -1):
                for widget in self.board_frame.grid_slaves(column=i):
                    widget.grid_forget()
                    widget.destroy()
        self.ui_collapse()

        self.unset_guard()

    def board_scale_trace(self) -> None:
        """Update the board square size."""
        self.set_guard()

        if self.board_scale.get() == self.SMALL_SCALE:
            self.board_square_size = self.ih.ImageSize.SM_SQUARE
        elif self.board_scale.get() == self.LARGE_SCALE:
            self.board_square_size = self.ih.ImageSize.LG_SQUARE
        self.board_square_size_px = int(self.board_square_size.value.split('x')[0])
        self.board_frame.config(
            height=self.board_square_size_px * self.rows.get(),
            width=self.board_square_size_px * self.columns.get(),
        )

        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            if square.enabled:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    'covered',
                )
            else:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    'unlocked',
                )
        self.ui_collapse()

        self.unset_guard()

    def ui_scale_trace(self) -> None:
        """Update the UI size."""
        self.set_guard()

        if self.ui_scale.get() == self.SMALL_SCALE:
            self.ui_square_size = self.ih.ImageSize.SM_SQUARE
            self.sevseg_size = self.ih.ImageSize.SM_SEVSEG
            self.style.configure(
                'FFMS.Toolbutton',
                font=self.SMALL_FONT,
                padding=('1.5m', '0.5m'),
            )
            self.style.configure(
                'FFMS.TLabel',
                font=self.SMALL_FONT,
            )
            self.style.configure(
                'FFMS.Toolbutton',
                font=self.SMALL_FONT,
                padding=('1.5m', '0.5m'),
            )
            self.style.configure(
                'FFMS.TEntry',
                font=self.SMALL_FONT,
            )
        elif self.ui_scale.get() == self.LARGE_SCALE:
            self.ui_square_size = self.ih.ImageSize.LG_SQUARE
            self.sevseg_size = self.ih.ImageSize.LG_SEVSEG
            self.style.configure(
                'FFMS.Toolbutton',
                font=self.LARGE_FONT,
                padding=('3m', '1m'),
            )
            self.style.configure(
                'FFMS.TLabel',
                font=self.LARGE_FONT,
            )
            self.style.configure(
                'FFMS.Toolbutton',
                font=self.LARGE_FONT,
                padding=('3m', '1m'),
            )
            self.style.configure(
                'FFMS.TEntry',
                font=self.LARGE_FONT,
            )

        for label in chain(
            self.flags_frame.grid_slaves(), self.timer_frame.grid_slaves()
        ):
            assert isinstance(label, ttk.Label)
            label.config(
                image=self.ih.lookup(
                    self.sevseg_size,
                    self.theme,
                    self.ih.ImageCategory.SEVSEG,
                    '0',
                )
            )
        self.mode_switch_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'uncover',
            ),
        )
        self.new_game_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'new',
            ),
        )
        self.leaderboard_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'leaderboard',
            ),
        )
        self.ui_collapse()

        self.unset_guard()

    def theme_option_trace(self) -> None:
        """Change the theme."""
        self.set_guard()
        if self.theme_option.get() == self.ih.ImageTheme.LIGHT.value:
            self.theme = self.ih.ImageTheme.LIGHT
            self.background_colour = self.LIGHT_BACKGROUND_COLOUR
            self.text_colour = self.LIGHT_TEXT_COLOUR
            self.ui_colour = self.LIGHT_UI_COLOUR
        elif self.theme_option.get() == self.ih.ImageTheme.DARK.value:
            self.theme = self.ih.ImageTheme.DARK
            self.background_colour = self.DARK_BACKGROUND_COLOUR
            self.text_colour = self.DARK_TEXT_COLOUR
            self.ui_colour = self.DARK_UI_COLOUR

        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            if square.enabled:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    'covered',
                )
            else:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    'unlocked',
                )

        for label in chain(
            self.flags_frame.grid_slaves(), self.timer_frame.grid_slaves()
        ):
            assert isinstance(label, ttk.Label)
            label.config(
                image=self.ih.lookup(
                    self.sevseg_size,
                    self.theme,
                    self.ih.ImageCategory.SEVSEG,
                    '0',
                )
            )
        self.mode_switch_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'uncover',
            ),
        )
        self.new_game_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'new',
            ),
        )
        self.leaderboard_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'leaderboard',
            ),
        )
        self.style.configure(
            'FFMS.TFrame',
            background=self.background_colour,
        )
        self.style.configure(
            'FFMS.Toolbutton',
            background=self.ui_colour,
            foreground=self.text_colour,
        )
        self.style.configure(
            'FFMS.TLabel',
            background=self.background_colour,
            foreground=self.text_colour,
        )
        self.style.configure(
            'FFMS.Treeview',
            background=self.background_colour,
            fieldbackground=self.background_colour,
            foreground=self.text_colour,
        )
        self.style.configure(
            'FFMS.TMenu',
            background=self.ui_colour,
            foreground=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        menu_q = [self.menubar]
        while menu_q:
            current_menu = menu_q.pop(0)
            for child in current_menu.children.values():
                if isinstance(child, tk.Menu):
                    menu_q.append(child)
            current_menu.config(
                font=self.SMALL_FONT,
                bg=self.ui_colour,
                fg=self.text_colour,
                activebackground=self.background_colour,
                activeforeground=self.text_colour,
                selectcolor=self.text_colour,
            )
        self.unset_guard()

    def multimine_trace(self) -> None:
        """Enter and exit multimine mode."""
        if self.multimine.get():
            self.max_flags = 5
        else:
            self.max_flags = 1

    def flagless_trace(self) -> None:
        """Enter and exit flagless mode."""
        if self.flagless.get():
            self.click_mode.set(self.ClickMode.FLAGLESS)
        else:
            self.click_mode.set(self.ClickMode.UNCOVER)

    def adaptive_ui_trace(self) -> None:
        """Respond to Adaptive UI setting."""
        if self.adaptive_ui.get():
            self.ui_collapse()
        elif not self.classic_ui.get():
            self.controls_frame.grid()
            self.menu_frame.grid_columnconfigure(5, weight=1)
            self.diff_frame.grid()
            self.menu_frame.grid_columnconfigure(4, weight=1)
            self.presets_frame.grid()
            self.menu_frame.grid_columnconfigure(0, weight=1)

    def click_mode_trace(self) -> None:
        if self.click_mode.get() == self.ClickMode.UNCOVER:
            self.mode_switch_button.config(
                image=self.ih.lookup(
                    self.ui_square_size,
                    self.theme,
                    self.ih.ImageCategory.UI,
                    'uncover',
                )
            )
        elif self.click_mode.get() == self.ClickMode.FLAG:
            self.mode_switch_button.config(
                image=self.ih.lookup(
                    self.ui_square_size,
                    self.theme,
                    self.ih.ImageCategory.UI,
                    'flag',
                )
            )

    def mode_key_behaviour_trace(self) -> None:
        if self.mode_key_behaviour.get() == 'hold':
            self.game_root.bind(
                '<KeyRelease-Shift_L>',
                self.toggle_click_mode,
            )
            self.ignore_toggle_key_held = True
        elif self.mode_key_behaviour.get() == 'toggle':
            self.game_root.unbind('<KeyRelease-Shift_L>')
            self.ignore_toggle_key_held = False
        self.mode_key_down = False

    def classic_ui_trace(self) -> None:
        if self.classic_ui.get():
            self.presets_frame.grid_remove()
            self.menu_frame.grid_columnconfigure(0, weight=0)

            self.diff_frame.grid_remove()
            self.menu_frame.grid_columnconfigure(4, weight=0)

            self.controls_frame.grid_remove()
            self.menu_frame.grid_columnconfigure(5, weight=0)

            self.leaderboard_button.grid_remove()
            self.new_game_button.grid_configure(padx=0)

            self.mode_switch_button.grid_remove()

            self.play_button.grid_remove()
        else:
            self.mode_switch_button.grid()
            self.play_button.grid()
            self.ui_collapse()

    def reset_settings(self) -> None:
        """Reset all game settings to defaults."""
        self.multimine.set(False)
        self.grace_rule.set(True)
        self.flagless.set(False)
        self.classic_ui.set(False)
        self.difficulty.set(self.DIFF_EASY)
        if self.board_scale.get() == self.SMALL_SCALE:
            self.board_scale.set(self.LARGE_SCALE)
        if self.ui_scale.get() == self.SMALL_SCALE:
            self.ui_scale.set(self.LARGE_SCALE)
        self.adaptive_ui.set(True)
        if self.rows.get() != 28:
            self.rows.set(28)
        if self.columns.get() != 30:
            self.columns.set(30)
        self.multimine_diff_inc.set(0.25)
        self.multimine_likelihood.set(0.5)
        self.theme_option.set(self.ih.ImageTheme.LIGHT.value)
        self.prompt_leaderboard_save.set(True)

    def check_for_updates(self) -> None:
        if self.rm.is_release_up_to_date():
            AcknowledgementDialogue(
                self.game_root,
                message='This release is up to date.',
            )
        else:
            self.rm.outdated_notice(force_message=True)

    # UI Generation Methods

    def init_style(self) -> None:
        """Set up style for the widgets."""
        self.style.theme_use('default')
        self.style.configure(
            'FFMS.TFrame',
            background=self.background_colour,
        )
        self.style.configure(
            'FFMS.Toolbutton',
            font=self.LARGE_FONT,
            relief='raised',
            padding=('3m', '1m'),
            anchor='center',
            background=self.ui_colour,
            foreground=self.text_colour,
        )
        self.style.configure(
            'FFMS.TLabel',
            font=self.LARGE_FONT,
            background=self.background_colour,
            anchor='center',
            borderwidth=0,
            foreground=self.text_colour,
        )
        self.style.configure(
            'Link.FFMS.TLabel',
            foreground='#0000ee',
        )
        self.style.configure(
            'FFMS.Treeview',
            font=self.LARGE_FONT,
            rowheight=64,
            background=self.background_colour,
            fieldbackground=self.background_colour,
            foreground=self.text_colour,
            borderwidth=0,
        )
        # There is no ttk.Menu widget. This acts as a pseudo-theme
        # so other areas of the code can access these settings
        self.style.configure(
            'FFMS.TMenu',
            background=self.ui_colour,
            foreground=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        self.main_frame.config(style='FFMS.TFrame')
        self.menu_frame.config(style='FFMS.TFrame')
        self.board_frame.config(style='FFMS.TFrame')
        self.presets_frame.config(style='FFMS.TFrame')
        self.flags_frame.config(style='FFMS.TFrame')
        self.mswpr_frame.config(style='FFMS.TFrame')
        self.timer_frame.config(style='FFMS.TFrame')
        self.diff_frame.config(style='FFMS.TFrame')
        self.controls_frame.config(style='FFMS.TFrame')
        self.mode_switch_button.config(style='FFMS.TLabel')
        self.new_game_button.config(style='FFMS.TLabel')
        self.play_button.config(style='FFMS.Toolbutton')
        self.stop_button.config(style='FFMS.Toolbutton')
        self.leaderboard_button.config(style='FFMS.TLabel')

    def init_window(self) -> None:
        """Set up window for the game."""
        self._hidden_root.withdraw()

        self.game_root.resizable(False, False)
        self.game_root.title('FreeForm Minesweeper (Loading...)')
        self.game_root.iconname('FreeForm Minesweeper')
        self.game_root.option_add('*tearOff', False)
        self.game_root.protocol('WM_DELETE_WINDOW', lambda: self.quit_game(False))
        self.game_root.iconphoto(
            False,
            self.ih.lookup(
                self.ih.ImageSize.LG_SQUARE,
                self.ih.ImageTheme.LIGHT,
                self.ih.ImageCategory.UI,
                'new',
            ),
        )

        self.board_frame.grid_propagate(False)
        self.main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.board_frame.config(
            height=self.board_square_size_px * self.rows.get(),
            width=self.board_square_size_px * self.columns.get(),
        )
        self.board_frame.grid(row=1, column=0, sticky=tk.NSEW)

    def init_keybinds(self) -> None:
        self.game_root.bind(
            '<Control-KeyPress-o>',
            lambda *_: self.load_board(),
        )
        self.game_root.bind(
            '<Control-KeyPress-s>',
            lambda *_: self.save_board(),
        )
        self.game_root.bind(
            '<Control-KeyPress-q>',
            lambda *_: self.quit_game(),
        )

        self.game_root.bind(
            '<Control-KeyPress-z>',
            lambda *_: self.undo_history(),
        )
        self.game_root.bind(
            '<Control-Shift-KeyPress-Z>',
            lambda *_: self.redo_history(),
        )
        self.game_root.bind(
            '<Control-KeyPress-f>',
            lambda *_: self.fill_board(),
        )
        self.game_root.bind(
            '<Control-KeyPress-x>',
            lambda *_: self.clear_board(),
        )
        self.game_root.bind(
            '<Control-KeyPress-i>',
            lambda *_: self.invert_board(),
        )
        self.game_root.bind(
            '<Control-KeyPress-c>',
            lambda *_: self.center_board(),
        )

        self.game_root.bind(
            '<KeyPress-Shift_L>',
            self.toggle_click_mode,
        )
        self.game_root.bind(
            '<KeyRelease-Shift_L>',
            self.toggle_click_mode,
        )

    def init_toolbar(self) -> None:
        self.menubar.config(
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
        )
        file_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        file_menu.add_command(
            label='Load Board',
            accelerator='Ctrl+O',
            command=self.load_board,
        )
        file_menu.add_command(
            label='Save Board',
            accelerator='Ctrl+S',
            command=self.save_board,
        )
        presets_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        presets_menu.add_command(
            label='Easy',
            command=lambda: self.load_board('presets/easy.ffmnswpr', self.DIFF_EASY),
        )
        presets_menu.add_command(
            label='Medium',
            command=lambda: self.load_board(
                'presets/medium.ffmnswpr', self.DIFF_MEDIUM
            ),
        )
        presets_menu.add_command(
            label='Hard',
            command=lambda: self.load_board('presets/hard.ffmnswpr', self.DIFF_HARD),
        )
        presets_menu.add_command(
            label='Expert',
            command=lambda: self.load_board(
                'presets/expert.ffmnswpr', self.DIFF_EXPERT
            ),
        )
        file_menu.add_cascade(label='Presets', menu=presets_menu)
        samples_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        samples_menu.add_command(
            label='Mine',
            command=lambda: self.load_board('sample_boards/mine.ffmnswpr'),
        )
        samples_menu.add_command(
            label='Flag',
            command=lambda: self.load_board('sample_boards/flag.ffmnswpr'),
        )
        samples_menu.add_command(
            label='Trophy',
            command=lambda: self.load_board('sample_boards/trophy.ffmnswpr'),
        )
        samples_menu.add_command(
            label='Win Face',
            command=lambda: self.load_board('sample_boards/winface.ffmnswpr'),
        )
        file_menu.add_cascade(label='Sample Boards', menu=samples_menu)
        file_menu.add_separator()
        file_menu.add_command(
            label='Leaderboard',
            command=lambda: LeaderboardViewDialogue(self.game_root),
        )
        file_menu.add_separator()
        file_menu.add_command(
            label='Quit Game',
            accelerator='Ctrl+Q',
            command=self.quit_game,
        )
        file_menu.add_separator()
        file_menu.add_command(label='Close')
        self.menubar.add_cascade(label='File', menu=file_menu)

        edit_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        edit_menu.add_command(
            label='Undo',
            accelerator='Ctrl+Z',
            command=self.undo_history,
        )
        edit_menu.add_command(
            label='Redo',
            accelerator='Ctrl+Shift+Z',
            command=self.redo_history,
        )
        edit_menu.add_command(
            label='Fill Board',
            accelerator='Ctrl+F',
            command=self.fill_board,
        )
        edit_menu.add_command(
            label='Clear Board',
            accelerator='Ctrl+X',
            command=self.clear_board,
        )
        edit_menu.add_command(
            label='Invert Board',
            accelerator='Ctrl+I',
            command=self.invert_board,
        )
        edit_menu.add_command(
            label='Center Board',
            accelerator='Ctrl+C',
            command=self.center_board,
        )
        edit_menu.add_separator()
        edit_menu.add_command(label='Close')
        self.menubar.add_cascade(label='Edit', menu=edit_menu)

        game_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        game_menu.add_command(label='Play Game', command=self.start_game)
        game_menu.add_command(
            label='Stop Playing',
            state=tk.DISABLED,
            command=self.stop_game,
        )
        game_menu.add_command(
            label='New Game',
            state=tk.DISABLED,
            command=self.new_game,
        )
        flagging_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        flagging_menu.add_radiobutton(
            label='Uncover Mines',
            value=self.ClickMode.UNCOVER,
            variable=self.click_mode,
        )
        flagging_menu.add_radiobutton(
            label='Place Flags',
            value=self.ClickMode.FLAG,
            variable=self.click_mode,
        )
        game_menu.add_cascade(
            label='Flagging Mode',
            state=tk.DISABLED,
            menu=flagging_menu,
        )
        shift_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        shift_menu.add_radiobutton(
            label='Hold (Left Shift)',
            value='hold',
            variable=self.mode_key_behaviour,
        )
        shift_menu.add_radiobutton(
            label='Toggle (Left Shift)',
            value='toggle',
            variable=self.mode_key_behaviour,
        )
        game_menu.add_cascade(label='Flag Mode Behaviour', menu=shift_menu)
        game_menu.add_checkbutton(
            label='Leaderboard Save Prompt',
            variable=self.prompt_leaderboard_save,
        )
        self.menubar.add_cascade(label='Game', menu=game_menu)

        options_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        options_menu.add_checkbutton(
            label='Multimine Mode',
            variable=self.multimine,
        )
        options_menu.add_checkbutton(
            label='Grace Rule',
            variable=self.grace_rule,
        )
        options_menu.add_checkbutton(
            label='Flagless',
            variable=self.flagless,
        )
        diff_menu = tk.Menu(
            options_menu,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        diff_menu.add_radiobutton(
            label=f'{self.DIFF_EASY:.0%} Mines',
            value=self.DIFF_EASY,
            variable=self.difficulty,
        )
        diff_menu.add_radiobutton(
            label=f'{self.DIFF_MEDIUM:.0%} Mines',
            value=self.DIFF_MEDIUM,
            variable=self.difficulty,
        )
        diff_menu.add_radiobutton(
            label=f'{self.DIFF_HARD:.0%} Mines',
            value=self.DIFF_HARD,
            variable=self.difficulty,
        )
        diff_menu.add_radiobutton(
            label=f'{self.DIFF_EXPERT:.0%} Mines',
            value=self.DIFF_EXPERT,
            variable=self.difficulty,
        )
        options_menu.add_cascade(label='Difficulty', menu=diff_menu)
        bds_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        bds_menu.add_radiobutton(
            label='Small',
            value=self.SMALL_SCALE,
            variable=self.board_scale,
        )
        bds_menu.add_radiobutton(
            label='Large',
            value=self.LARGE_SCALE,
            variable=self.board_scale,
        )
        options_menu.add_cascade(label='Board Scale', menu=bds_menu)
        uis_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        uis_menu.add_radiobutton(
            label='Small',
            value=self.SMALL_SCALE,
            variable=self.ui_scale,
        )
        uis_menu.add_radiobutton(
            label='Large',
            value=self.LARGE_SCALE,
            variable=self.ui_scale,
        )
        options_menu.add_cascade(label='UI Scale', menu=uis_menu)
        options_menu.add_checkbutton(
            label='Adaptive UI',
            variable=self.adaptive_ui,
        )
        options_menu.add_checkbutton(
            label='Classic UI',
            variable=self.classic_ui,
        )
        theme_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        theme_menu.add_radiobutton(
            label='Light',
            value=self.ih.ImageTheme.LIGHT.value,
            variable=self.theme_option,
        )
        theme_menu.add_radiobutton(
            label='Dark',
            value=self.ih.ImageTheme.DARK.value,
            variable=self.theme_option,
        )
        options_menu.add_cascade(label='Theme', menu=theme_menu)
        options_menu.add_separator()
        options_menu.add_command(
            label='More...',
            command=lambda: SettingsDialogue(
                self.game_root,
                {
                    'Rows': (3, 64, 1, self.rows),
                    'Columns': (3, 64, 1, self.columns),
                    'MultiMine Difficulty Increase': (
                        0.0,
                        0.5,
                        0.01,
                        self.multimine_diff_inc,
                    ),
                    'MultiMine Probability': (
                        0.0,
                        1.0,
                        0.01,
                        self.multimine_likelihood,
                    ),
                },
            ),
        )
        options_menu.add_separator()
        options_menu.add_command(label='Reset Settings', command=self.reset_settings)
        options_menu.add_separator()
        options_menu.add_command(label='Close')
        self.menubar.add_cascade(label='Options', menu=options_menu)

        help_menu = tk.Menu(
            self.menubar,
            font=self.SMALL_FONT,
            bg=self.ui_colour,
            fg=self.text_colour,
            activebackground=self.background_colour,
            activeforeground=self.text_colour,
            selectcolor=self.text_colour,
        )
        help_menu.add_command(
            label='About...',
            command=lambda: AcknowledgementWithLinkDialogue(
                self.game_root,
                (
                    f'FreeForm Minesweeper ({self.rm.version}), created by KittyKittyKitKat.\n'
                    'Check out my GitHub!'
                ),
                ('GitHub Page', self.GITHUB_PAGE),
                title='FreeForm Minesweeper About',
            ),
        )
        help_menu.add_command(
            label='Tutorial',
            command=lambda: AcknowledgementWithLinkDialogue(
                self.game_root,
                'Click the link to open the tutorial page in your browser.',
                ('Tutorial', self.TUTORIAL_PAGE),
                title='FreeForm Minesweeper Help',
            ),
        )
        help_menu.add_command(
            label='Check for Updates',
            command=self.check_for_updates,
        )
        help_menu.add_command(
            label='Copyright',
            command=lambda: AcknowledgementDialogue(
                self.game_root,
                'Copyright \N{COPYRIGHT SIGN} Simon Harris-Palmer 2023. All rights reserved.',
                title='FreeForm Minesweeper Copyright',
            ),
        )
        help_menu.add_separator()
        help_menu.add_command(label='Close')
        self.menubar.add_cascade(label='Help', menu=help_menu)

        self.game_root.config(menu=self.menubar)

    def init_menu(self) -> None:
        """Set up menu for the game"""
        self.menu_frame.config(padding=(0, self.UI_PADDING, 0))
        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_columnconfigure(1, weight=1)
        self.menu_frame.grid_columnconfigure(2, weight=1)
        self.menu_frame.grid_columnconfigure(3, weight=1)
        self.menu_frame.grid_columnconfigure(4, weight=1)
        self.menu_frame.grid_columnconfigure(5, weight=1)

        self.presets_frame.grid_columnconfigure(0, weight=1)
        self.presets_frame.grid_columnconfigure(1, weight=1)
        preset_easy = ttk.Button(
            self.presets_frame,
            text='Easy',
            width=6,
            style='FFMS.Toolbutton',
            command=lambda: self.load_board('presets/easy.ffmnswpr', self.DIFF_EASY),
            takefocus=False,
            cursor='hand2',
        )
        preset_medium = ttk.Button(
            self.presets_frame,
            text='Medium',
            width=6,
            style='FFMS.Toolbutton',
            command=lambda: self.load_board(
                'presets/medium.ffmnswpr', self.DIFF_MEDIUM
            ),
            takefocus=False,
            cursor='hand2',
        )
        preset_hard = ttk.Button(
            self.presets_frame,
            text='Hard',
            width=6,
            style='FFMS.Toolbutton',
            command=lambda: self.load_board('presets/hard.ffmnswpr', self.DIFF_HARD),
            takefocus=False,
            cursor='hand2',
        )
        preset_expert = ttk.Button(
            self.presets_frame,
            text='Expert',
            width=6,
            style='FFMS.Toolbutton',
            command=lambda: self.load_board(
                'presets/expert.ffmnswpr', self.DIFF_EXPERT
            ),
            takefocus=False,
            cursor='hand2',
        )
        preset_easy.grid(row=0, column=0, sticky=tk.NSEW)
        preset_medium.grid(row=0, column=1, sticky=tk.NSEW)
        preset_hard.grid(row=1, column=0, sticky=tk.NSEW)
        preset_expert.grid(row=1, column=1, sticky=tk.NSEW)
        self.presets_frame.grid(row=0, column=0)

        self.flags_frame.grid_columnconfigure(0, weight=1)
        self.flags_frame.grid_columnconfigure(1, weight=1)
        self.flags_frame.grid_columnconfigure(2, weight=1)
        flag_left = ttk.Label(
            self.flags_frame,
            image=self.ih.lookup(
                self.sevseg_size,
                self.theme,
                self.ih.ImageCategory.SEVSEG,
                '0',
            ),
            style='FFMS.TLabel',
        )
        flag_mid = ttk.Label(
            self.flags_frame,
            image=self.ih.lookup(
                self.sevseg_size,
                self.theme,
                self.ih.ImageCategory.SEVSEG,
                '0',
            ),
            style='FFMS.TLabel',
        )
        flag_right = ttk.Label(
            self.flags_frame,
            image=self.ih.lookup(
                self.sevseg_size,
                self.theme,
                self.ih.ImageCategory.SEVSEG,
                '0',
            ),
            style='FFMS.TLabel',
        )
        flag_left.grid(row=0, column=0, sticky=tk.NSEW)
        flag_mid.grid(row=0, column=1, sticky=tk.NSEW)
        flag_right.grid(row=0, column=2, sticky=tk.NSEW)
        self.flags_frame.grid(row=0, column=1)

        self.mode_switch_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'uncover',
            ),
            cursor='hand2',
        )
        self.mode_switch_button.bind('<Button-1>', self.toggle_click_mode)
        self.mode_switch_button.state([tk.DISABLED])
        self.new_game_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'new',
            ),
            cursor='hand2',
        )
        self.new_game_button.state([tk.DISABLED])

        def hold():
            if self.state is not self.State.DRAW:
                self.new_game_button.config(
                    image=self.ih.lookup(
                        self.ui_square_size,
                        self.theme,
                        self.ih.ImageCategory.UI,
                        'held',
                    )
                )

        self.new_game_button.bind('<Button-1>', lambda *_: hold())
        self.new_game_button.bind('<ButtonRelease-1>', lambda *_: self.new_game())
        self.leaderboard_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'leaderboard',
            ),
            command=lambda *_: LeaderboardViewDialogue(self.game_root),
            takefocus=False,
            cursor='hand2',
        )
        self.play_button.config(
            text='Play',
            width=5,
            command=self.start_game,
            takefocus=False,
            cursor='hand2',
        )
        self.stop_button.config(
            text='Stop',
            width=5,
            command=self.stop_game,
            takefocus=False,
            cursor='hand2',
        )

        self.mswpr_frame.grid_columnconfigure(0, weight=1)
        self.mswpr_frame.grid_columnconfigure(1, weight=1)
        self.mswpr_frame.grid_columnconfigure(2, weight=1)
        self.mode_switch_button.grid(row=0, column=0, pady=3, sticky=tk.NSEW)
        self.new_game_button.grid(
            row=0,
            column=1,
            padx=self.UI_PADDING,
            pady=3,
            sticky=tk.NSEW,
        )
        self.leaderboard_button.grid(row=0, column=2, pady=3, sticky=tk.NSEW)
        self.stop_button.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)
        self.stop_button.grid_remove()
        self.play_button.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)
        self.mswpr_frame.grid(row=0, column=2)

        self.timer_frame.grid_columnconfigure(0, weight=1)
        self.timer_frame.grid_columnconfigure(1, weight=1)
        self.timer_frame.grid_columnconfigure(2, weight=1)
        timer_left = ttk.Label(
            self.timer_frame,
            image=self.ih.lookup(
                self.sevseg_size,
                self.theme,
                self.ih.ImageCategory.SEVSEG,
                '0',
            ),
            style='FFMS.TLabel',
        )
        timer_mid = ttk.Label(
            self.timer_frame,
            image=self.ih.lookup(
                self.sevseg_size,
                self.theme,
                self.ih.ImageCategory.SEVSEG,
                '0',
            ),
            style='FFMS.TLabel',
        )
        timer_right = ttk.Label(
            self.timer_frame,
            image=self.ih.lookup(
                self.sevseg_size,
                self.theme,
                self.ih.ImageCategory.SEVSEG,
                '0',
            ),
            style='FFMS.TLabel',
        )
        timer_left.grid(row=0, column=0, sticky=tk.NSEW)
        timer_mid.grid(row=0, column=1, sticky=tk.NSEW)
        timer_right.grid(row=0, column=2, sticky=tk.NSEW)
        self.timer_frame.grid(row=0, column=3)

        self.diff_frame.grid_columnconfigure(0, weight=1)
        self.diff_frame.grid_columnconfigure(1, weight=1)
        self.diff_frame.grid_columnconfigure(2, weight=1)
        self.diff_frame.grid_columnconfigure(3, weight=1)
        diff_label = ttk.Label(
            self.diff_frame,
            text='Difficulty',
            style='FFMS.TLabel',
        )
        diff_1 = ttk.Radiobutton(
            self.diff_frame,
            text='1',
            width=1,
            value=self.DIFF_EASY,
            variable=self.difficulty,
            style='FFMS.Toolbutton',
            takefocus=False,
            cursor='hand2',
        )
        diff_2 = ttk.Radiobutton(
            self.diff_frame,
            text='2',
            width=1,
            value=self.DIFF_MEDIUM,
            variable=self.difficulty,
            style='FFMS.Toolbutton',
            takefocus=False,
            cursor='hand2',
        )
        diff_3 = ttk.Radiobutton(
            self.diff_frame,
            text='3',
            value=self.DIFF_HARD,
            variable=self.difficulty,
            style='FFMS.Toolbutton',
            takefocus=False,
            cursor='hand2',
        )
        diff_4 = ttk.Radiobutton(
            self.diff_frame,
            text='4',
            value=self.DIFF_EXPERT,
            variable=self.difficulty,
            style='FFMS.Toolbutton',
            takefocus=False,
            cursor='hand2',
        )

        diff_label.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky=tk.NSEW,
            pady=(0, self.UI_PADDING),
        )
        diff_1.grid(row=1, column=0, sticky=tk.NSEW)
        diff_2.grid(row=1, column=1, sticky=tk.NSEW)
        diff_3.grid(row=1, column=2, sticky=tk.NSEW)
        diff_4.grid(row=1, column=3, sticky=tk.NSEW)
        self.diff_frame.grid(row=0, column=4)

        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1)
        fill_button = ttk.Button(
            self.controls_frame,
            text='Fill',
            width=6,
            style='FFMS.Toolbutton',
            command=self.fill_board,
            takefocus=False,
            cursor='hand2',
        )
        clear_button = ttk.Button(
            self.controls_frame,
            text='Clear',
            width=6,
            style='FFMS.Toolbutton',
            command=self.clear_board,
            takefocus=False,
            cursor='hand2',
        )
        invert_board_button = ttk.Button(
            self.controls_frame,
            text='Invert',
            width=6,
            style='FFMS.Toolbutton',
            command=self.invert_board,
            takefocus=False,
            cursor='hand2',
        )
        center_board_button = ttk.Button(
            self.controls_frame,
            text='Center',
            width=6,
            style='FFMS.Toolbutton',
            command=self.center_board,
            takefocus=False,
            cursor='hand2',
        )

        fill_button.grid(row=0, column=1, sticky=tk.NSEW)
        clear_button.grid(row=1, column=1, sticky=tk.NSEW)
        invert_board_button.grid(row=0, column=2, sticky=tk.NSEW)
        center_board_button.grid(row=1, column=2, sticky=tk.NSEW)
        self.controls_frame.grid(row=0, column=5)

        self.menu_frame.grid(row=0, column=0, sticky=tk.NSEW)

    def init_board(self) -> None:
        """Set up the squares on the board."""

        for x in range(self.rows.get()):
            for y in range(self.columns.get()):
                # self.game_root.update_idletasks()
                self.make_square(x, y)

    def make_square(self, row: int, column: int) -> None:
        """Make a BoardSquare and place it in the grid"""
        self.game_root.update_idletasks()
        sq = BoardSquare(
            self.board_frame,
            self.ih.lookup(
                self.board_square_size,
                self.theme,
                self.ih.ImageCategory.BOARD,
                'unlocked',
            ),
            'FFMS.TLabel',
        )
        sq.bind('<Button-1>', self.left_mouse_press_handler)
        sq.bind('<Button-3>', self.right_mouse_press_handler)
        sq.bind('<B1-Motion>', self.mouse_motion_handler)
        sq.bind('<ButtonRelease-1>', self.mouse_release_handler)
        sq.bind('<Double-Button-1>', self.double_mouse_handler)
        sq.grid(row=row, column=column)

    # UI Interaction Methods

    def quit_game(self, ask: bool = True) -> None:
        a = tk.BooleanVar()
        if ask:
            YesNoDialogue(
                self.game_root,
                question='Are you sure you want to quit?',
                answer=a,
            )
        else:
            a.set(True)
        if a.get():
            self.game_root.withdraw()
            self._hidden_root.destroy()
            self.alive = False

    def lock_toolbar(self) -> None:
        """Configure toolbar for options designed for sweeping mode."""
        self.menubar.entryconfigure('File', state=tk.DISABLED)
        self.menubar.entryconfigure('Edit', state=tk.DISABLED)
        self.menubar.entryconfigure('Options', state=tk.DISABLED)
        game_submenu: tk.Menu = self.game_root.nametowidget(
            self.menubar.entrycget('Game', 'menu')
        )
        game_submenu.entryconfigure('Play Game', state=tk.DISABLED)
        game_submenu.entryconfigure('Stop Playing', state=tk.NORMAL)
        game_submenu.entryconfigure('New Game', state=tk.NORMAL)
        if self.click_mode.get() != self.ClickMode.FLAGLESS:
            game_submenu.entryconfigure('Flagging Mode', state=tk.NORMAL)

    def unlock_toolbar(self) -> None:
        """Configure toolbar for options designed for drawing mode."""
        self.menubar.entryconfigure('File', state=tk.NORMAL)
        self.menubar.entryconfigure('Edit', state=tk.NORMAL)
        self.menubar.entryconfigure('Options', state=tk.NORMAL)
        game_submenu: tk.Menu = self.game_root.nametowidget(
            self.menubar.entrycget('Game', 'menu')
        )
        game_submenu.entryconfigure('Play Game', state=tk.NORMAL)
        game_submenu.entryconfigure('Stop Playing', state=tk.DISABLED)
        game_submenu.entryconfigure('New Game', state=tk.DISABLED)
        game_submenu.entryconfigure('Flagging Mode', state=tk.DISABLED)

    def set_guard(self) -> None:
        """Disable the UI while important events occur."""
        self.game_root.title('FreeForm Minesweeper (Loading...)')
        self.state = self.State.PAUSE
        self.lock_toolbar()
        for button in self.get_menu_buttons:
            assert isinstance(button, ttk.Widget)
            button.state(['disabled'])

    def unset_guard(self) -> None:
        """Enable the UI."""
        for button in self.get_menu_buttons:
            assert isinstance(button, ttk.Widget)
            if button not in (self.new_game_button, self.mode_switch_button):
                button.state(['!disabled'])
        self.unlock_toolbar()
        self.state = self.State.DRAW
        self.game_root.title('FreeForm Minesweeper')

    def ui_collapse(self) -> None:
        """Hide/show parts of the UI depending on the board size."""
        if not self.adaptive_ui.get():
            return
        thresholds_lb_lu = (22, 17, 13, 9)
        thresholds_lb_su = (14, 11, 8, 5)
        thresholds_sb_lu = (43, 34, 26, 17)
        thresholds_sb_su = (27, 21, 16, 9)
        bs = self.board_scale.get()
        us = self.ui_scale.get()
        if bs == self.LARGE_SCALE and us == self.LARGE_SCALE:
            thresholds = thresholds_lb_lu
        elif bs == self.LARGE_SCALE and us == self.SMALL_SCALE:
            thresholds = thresholds_lb_su
        elif bs == self.SMALL_SCALE and us == self.LARGE_SCALE:
            thresholds = thresholds_sb_lu
        elif bs == self.SMALL_SCALE and us == self.SMALL_SCALE:
            thresholds = thresholds_sb_su

        curr_columns = self.columns.get()
        if curr_columns < thresholds[0]:
            self.controls_frame.grid_remove()
            self.menu_frame.grid_columnconfigure(5, weight=0)
        elif not self.classic_ui.get():
            self.controls_frame.grid()
            self.menu_frame.grid_columnconfigure(5, weight=1)

        if curr_columns < thresholds[1]:
            self.diff_frame.grid_remove()
            self.menu_frame.grid_columnconfigure(4, weight=0)
        elif not self.classic_ui.get():
            self.diff_frame.grid()
            self.menu_frame.grid_columnconfigure(4, weight=1)

        if curr_columns < thresholds[2]:
            self.presets_frame.grid_remove()
            self.menu_frame.grid_columnconfigure(0, weight=0)
        elif not self.classic_ui.get():
            self.presets_frame.grid()
            self.menu_frame.grid_columnconfigure(0, weight=1)

        if curr_columns < thresholds[3]:
            self.leaderboard_button.grid_remove()
            self.new_game_button.grid_configure(padx=0)
        elif not self.classic_ui.get():
            self.leaderboard_button.grid()
            self.new_game_button.grid_configure(padx=self.UI_PADDING)

    def sweep_click_hold_handler(self, square: BoardSquare) -> None:
        if not square.enabled or not square.covered:
                return
        self.new_game_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'shocked',
            )
        )
        if self.currently_held_square is not None:
            self.currently_held_square.image = self.ih.lookup(
                self.board_square_size,
                self.theme,
                self.ih.ImageCategory.BOARD,
                'covered',
            )
        self.currently_held_square = square
        square.image = self.ih.lookup(
            self.board_square_size,
            self.theme,
            self.ih.ImageCategory.BOARD,
            '0',
        )

    def left_mouse_press_handler(self, event: tk.Event) -> None:
        """Handle mouse press events in the board.

        Args:
            event: Tkinter event.
        """
        square: BoardSquare = event.widget
        if self.state is self.State.DRAW:
            self.square_toggle_enabled(square)
            self.draw_history_step.append(square)
        elif self.state is self.State.SWEEP:
            self.sweep_click_hold_handler(square)

    def right_mouse_press_handler(self, event: tk.Event) -> None:
        """Handle mouse press events in the board.

        Args:
            event: Tkinter event.
        """
        square: BoardSquare = event.widget
        if self.state is self.State.SWEEP:
            if self.click_mode.get() == self.ClickMode.UNCOVER:
                if not self.multimine.get():
                    if square.flag_count:
                        self.remove_flag(square)
                    else:
                        self.add_flag(square)
            elif self.click_mode.get() == self.ClickMode.FLAG:
                self.remove_flag(square)

    def mouse_release_handler(self, event: tk.Event) -> None:
        """Handle mouse release events in the board.

        Args:
            event: Tkinter event.
        """
        if self.state is self.State.DRAW:
            self.inc_history()
        elif self.state is self.State.SWEEP:
            square = self.currently_held_square
            if square is None:
                return
            x = (
                event.x_root - square.master.winfo_rootx()
            ) // self.board_square_size_px
            y = (
                event.y_root - square.master.winfo_rooty()
            ) // self.board_square_size_px
            square = None
            if y in range(self.rows.get()) and x in range(self.columns.get()):
                square = self.board_frame.grid_slaves(row=y, column=x)[0]

            if square is None or not square.enabled or not square.covered:
                self.new_game_button.config(
                    image=self.ih.lookup(
                        self.ui_square_size,
                        self.theme,
                        self.ih.ImageCategory.UI,
                        'new',
                    )
                )
                if self.currently_held_square is not None:
                    self.currently_held_square.image = self.ih.lookup(
                        self.ui_square_size,
                        self.theme,
                        self.ih.ImageCategory.BOARD,
                        'covered',
                    )
                    self.currently_held_square = None
                return

            self.currently_held_square = None
            self.new_game_button.config(
                image=self.ih.lookup(
                    self.ui_square_size,
                    self.theme,
                    self.ih.ImageCategory.UI,
                    'new',
                )
            )
            if self.click_mode.get() in (
                self.ClickMode.UNCOVER,
                self.ClickMode.FLAGLESS,
            ):
                if not square.enabled or square.flag_count:
                    return
                self.uncover_square(square)
                if square.mine_count:
                    return
                if square.value == 0:
                    self.chord(square)
                if self.squares_cleared == self.squares_to_win:
                    self.game_won()
            elif self.click_mode.get() == self.ClickMode.FLAG:
                self.add_flag(square)

    def double_mouse_handler(self, event: tk.Event) -> None:
        """Handle double mouse press events in the board.

        Args:
            event: Tkinter event.
        """
        square: BoardSquare = event.widget
        if self.state is self.State.DRAW:
            self.square_toggle_enabled(square)
            self.draw_history_step.append(square)
        elif self.state is not self.State.PAUSE and not square.covered:
            flags_around = 0
            for neighbour in square.neighbours.values():
                if neighbour:
                    flags_around += neighbour.flag_count
            if flags_around == square.value:
                self.chord(square, force=True)
            if self.squares_cleared == self.squares_to_win:
                self.game_won()
        elif (
            self.state is self.State.SWEEP
            and self.click_mode.get() == self.ClickMode.FLAG
        ):
            self.add_flag(square)

    def mouse_motion_handler(self, event: tk.Event) -> None:
        """Handle mouse motion events in the board.

        Args:
            event: Tkinter event.
        """
        initial_square: BoardSquare = event.widget
        x = (
                event.x_root - initial_square.master.winfo_rootx()
        ) // self.board_square_size_px
        y = (
            event.y_root - initial_square.master.winfo_rooty()
        ) // self.board_square_size_px
        square = None
        if y in range(self.rows.get()) and x in range(self.columns.get()):
            square = self.board_frame.grid_slaves(row=y, column=x)[0]

        if not isinstance(square, BoardSquare):
            return

        if self.state is self.State.DRAW:
            if square.enabled != initial_square.enabled:
                self.square_toggle_enabled(square)
                self.draw_history_step.append(square)
        elif self.state is self.State.SWEEP:
            if self.currently_held_square is not None:
                self.sweep_click_hold_handler(square)

    def inc_history(self) -> None:
        """Add the current history step to the history."""
        self.draw_history.append(self.draw_history_step.copy())
        if (
            self.draw_history_buffer
            and self.draw_history_step == self.draw_history_buffer[-1]
        ):
            self.draw_history_buffer.pop(-1)
        else:
            self.draw_history_buffer.clear()
        self.draw_history_step.clear()

    def undo_history(self) -> None:
        """Move to the previous point in history."""
        if self.state is not self.State.DRAW:
            return
        if not self.draw_history:
            return
        step = self.draw_history.pop(-1)
        self.draw_history_buffer.append(step)
        for square in step:
            self.square_toggle_enabled(square)

    def redo_history(self) -> None:
        """Move to the next point in the history buffer."""
        if self.state is not self.State.DRAW:
            return
        if not self.draw_history_buffer:
            return
        step = self.draw_history_buffer.pop(-1)
        self.draw_history.append(step)
        for square in step:
            self.square_toggle_enabled(square)

    def clear_history(self) -> None:
        """Clear all the drawing history data."""
        self.draw_history.clear()
        self.draw_history_step.clear()
        self.draw_history_buffer.clear()

    def compress_board(self) -> list[str]:
        """Compress the current board to its smallest possible form.

        Returns:
            A list of bit strings representing a game board.
        """
        leftmost = self.columns.get() - 1
        board_bits: list[str] = []
        reached_content = False
        for row in range(self.rows.get()):
            bit_row = ''
            for col in range(self.columns.get()):
                square = self.board_frame.grid_slaves(row=row, column=col)[0]
                assert isinstance(square, BoardSquare)
                bit_row += '1' if square.enabled else '0'
            if '1' in bit_row:
                leftmost_index = bit_row.index('1')
                rightmost_index = bit_row.rindex('1') + 1
                leftmost = min(leftmost_index, leftmost)
                reached_content = True
                board_bits.append(bit_row[:rightmost_index])
            elif '1' not in bit_row and reached_content:
                board_bits.append('0')
        last_content_index = len(board_bits)
        for i, bit_row in enumerate(reversed(board_bits)):
            if '1' in bit_row:
                last_content_index -= i
                break
        board_bits = board_bits[:last_content_index]
        for i, bit_row in enumerate(board_bits):
            if bit_row != '0':
                board_bits[i] = bit_row[leftmost:]
        return board_bits

    def compress_board_rle(self) -> str:
        """Compress the current board to its smallest possible form.

        Returns:
            Run length encoded string representing a game board.
        """
        board_bits = self.compress_board()
        board_txt = 'N'.join(board_bits).replace('1', 'E').replace('0', 'D')
        board_rle = ''.join(str(len(list(g))) + k for k, g in groupby(board_txt))
        return board_rle

    @cached_property
    def get_menu_buttons(self) -> list[tk.Widget]:
        """Get all the buttons present in the menu."""
        return list(
            chain(
                self.presets_frame.grid_slaves(),
                self.mswpr_frame.grid_slaves(),
                (
                    widget
                    for widget in self.diff_frame.grid_slaves()
                    if not isinstance(widget, ttk.Label)
                ),
                self.controls_frame.grid_slaves(),
            )
        )

    def update_timer(self) -> None:
        """Update timer widgets."""
        seconds = list(str(int(self.time_elapsed)).zfill(3))
        for number in self.timer_frame.grid_slaves():
            assert isinstance(number, ttk.Label)
            number.config(
                image=self.ih.lookup(
                    self.sevseg_size,
                    self.theme,
                    self.ih.ImageCategory.SEVSEG,
                    seconds.pop(),
                )
            )

    def reset_timer(self) -> None:
        """Reset timer widgets."""
        for number in self.timer_frame.grid_slaves():
            assert isinstance(number, ttk.Label)
            number.config(
                image=self.ih.lookup(
                    self.sevseg_size,
                    self.theme,
                    self.ih.ImageCategory.SEVSEG,
                    '0',
                ),
            )

    def update_flag_counter(self) -> None:
        """Update flag widgets."""
        flags = list(str(self.num_mines - self.flags_placed).zfill(3))
        for number in self.flags_frame.grid_slaves():
            assert isinstance(number, ttk.Label)
            number.config(
                image=self.ih.lookup(
                    self.sevseg_size,
                    self.theme,
                    self.ih.ImageCategory.SEVSEG,
                    flags.pop(),
                )
            )

    def reset_flag_counter(self) -> None:
        """Reset flag widgets."""
        for number in self.flags_frame.grid_slaves():
            assert isinstance(number, ttk.Label)
            number.config(
                image=self.ih.lookup(
                    self.sevseg_size,
                    self.theme,
                    self.ih.ImageCategory.SEVSEG,
                    '0',
                ),
            )

    # Gameplay methods

    def square_toggle_enabled(self, square: BoardSquare) -> None:
        """Toggle a square's enabled status and update its image.

        Args:
            square: Square to toggle.
        """
        square.toggle_enable()
        if square.enabled:
            square.image = self.ih.lookup(
                self.board_square_size,
                self.theme,
                self.ih.ImageCategory.BOARD,
                'covered',
            )
        else:
            square.image = self.ih.lookup(
                self.board_square_size,
                self.theme,
                self.ih.ImageCategory.BOARD,
                'unlocked',
            )

    def uncover_square(self, square: BoardSquare) -> None:
        """Uncover a square and update its image.

        Args:
            square: Square to uncover.
        """
        if square.mine_count and not square.flag_count:
            if self.grace_rule.get() and self.squares_cleared == 0:
                self.new_game()
                self.uncover_square(square)
                return
            square.image = self.ih.lookup(
                self.board_square_size,
                self.theme,
                self.ih.ImageCategory.BOARD,
                f'mine_{square.mine_count}_explode',
            )
            square.uncover()
            self.game_lost()
        elif square.covered and not square.flag_count:
            square.calculate_value()
            square.uncover()
            square.image = self.ih.lookup(
                self.board_square_size,
                self.theme,
                self.ih.ImageCategory.BOARD,
                str(square.value),
            )
            self.squares_cleared += 1

    def chord(self, square: BoardSquare, force: bool = False) -> None:
        """Chord a square.

        Args:
            square: The square to chord.
            force: Force chording even if the clicked square is not 0.
                This only applied to the clicked square, not any neighbours.
                Defaults to False.
        """
        chord_q = {square}
        while chord_q:
            curr_square = chord_q.pop()
            self.uncover_square(curr_square)
            if curr_square.value == 0 or force:
                force = False
                for n_sq in curr_square.neighbours.values():
                    if n_sq and n_sq.covered:
                        chord_q.add(n_sq)

    def link_squares_neighbours(self, square: BoardSquare) -> None:
        """Link a square to its eight potential neighbours.

        Args:
            square: The square being given neighbours.
        """
        dirs = square.directions
        square_row, square_col = square.position
        k = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0:
                    continue
                curr_direction = dirs[k]
                k += 1
                check_x = i + square_row
                check_y = j + square_col
                if check_x in range(self.rows.get()) and check_y in range(
                    self.columns.get()
                ):
                    child_widget = self.board_frame.grid_slaves(
                        row=check_x, column=check_y
                    )[0]
                    if isinstance(child_widget, BoardSquare) and child_widget.enabled:
                        square.neighbours[curr_direction] = child_widget
                    else:
                        square.neighbours[curr_direction] = None

    def toggle_click_mode(self, event: tk.Event | None = None) -> None:
        """Toggle the clicking mode of the game."""
        if self.state is self.State.DRAW:
            return
        if self.click_mode.get() == self.ClickMode.FLAGLESS:
            return
        if event is not None:
            if event.type is tk.EventType.KeyPress:
                if self.mode_key_down and self.ignore_toggle_key_held:
                    return
                self.mode_key_down = True
            elif event.type is tk.EventType.KeyRelease:
                self.mode_key_down = False
        if self.click_mode.get() == self.ClickMode.UNCOVER:
            self.click_mode.set(self.ClickMode.FLAG)
        elif self.click_mode.get() == self.ClickMode.FLAG:
            self.click_mode.set(self.ClickMode.UNCOVER)

    def fill_board(self) -> None:
        """Make all squares enabled."""
        if self.state is not self.State.DRAW:
            return
        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            if not square.enabled:
                self.square_toggle_enabled(square)
                self.draw_history_step.append(square)
        self.inc_history()

    def clear_board(self) -> None:
        """Make all squares disabled."""
        if self.state is not self.State.DRAW:
            return
        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            if square.enabled:
                self.square_toggle_enabled(square)
                self.draw_history_step.append(square)
        self.inc_history()

    def invert_board(self) -> None:
        """Toggle all the squares on the board between enabled and disabled."""
        if self.state is not self.State.DRAW:
            return
        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            self.square_toggle_enabled(square)
            self.draw_history_step.append(square)
        self.inc_history()

    def center_board(self) -> None:
        if self.state is not self.State.DRAW:
            return

        board_bits = self.compress_board()
        if not board_bits:
            return
        longest_row_len = len(max(board_bits, key=len))
        padded_right_bits = [row.ljust(longest_row_len, '0') for row in board_bits]
        columns = self.columns.get()
        centered_board_bits = [row.center(columns, '0') for row in padded_right_bits]
        rows = self.rows.get()
        num_empty_rows = rows - len(centered_board_bits)
        num_rows_before = num_empty_rows // 2
        num_rows_after = num_empty_rows - num_rows_before
        for _ in range(num_rows_before):
            centered_board_bits.insert(0, '0' * columns)
        for _ in range(num_rows_after):
            centered_board_bits.append('0' * columns)
        bit_string = ''.join(centered_board_bits)
        for square, bit in zip(self.board_frame.grid_slaves(), reversed(bit_string)):
            if isinstance(square, BoardSquare) and square.enabled != bool(int(bit)):
                self.square_toggle_enabled(square)
                self.draw_history_step.append(square)
        self.inc_history()

    def load_board(
        self,
        filename: str | None = None,
        difficulty: float | None = None,
    ) -> None:
        """Load an external board into the game.

        Args:
            filename: Name of the board file to load.
            difficulty: Associated game difficulty for board loaded.
        """
        if self.state is not self.State.DRAW:
            return
        board_file = filename or filedialog.askopenfilename(
            initialdir=self.SAVE_LOAD_DIR, title='Open Board', filetypes=self.FILE_TYPE
        )
        if not board_file:
            return
        try:
            with open(board_file, 'r') as board_load_file:
                board_bits = [
                    line.strip()
                    for line in board_load_file.readlines()
                    if not line.startswith('#')
                ]
        except Exception:
            AcknowledgementDialogue(
                self.game_root,
                'Was not able to open the file.',
            )
            return
        if (
            len(board_bits) > self.rows.get()
            or len(max(board_bits, key=len)) > self.columns.get()
        ):
            AcknowledgementDialogue(
                self.game_root,
                'Board was too large to be loaded properly',
            )
            return
        self.clear_board()
        for curr_row, bit_row in enumerate(board_bits):
            for curr_col, bit in enumerate(bit_row):
                if bit == '1':
                    square = self.board_frame.grid_slaves(
                        row=curr_row, column=curr_col
                    )[0]
                    assert isinstance(square, BoardSquare)
                    self.square_toggle_enabled(square)
        self.clear_history()
        if difficulty:
            self.difficulty.set(difficulty)

    def save_board(self) -> None:
        """Save the current board to a file."""
        if self.state is not self.State.DRAW:
            return
        compressed_board = self.compress_board()
        board_file = filedialog.asksaveasfilename(
            initialdir=self.SAVE_LOAD_DIR,
            title='Save Board',
            filetypes=self.FILE_TYPE,
            defaultextension=self.FILE_EXTENSION,
        )
        if not board_file:
            return
        if not board_file.endswith(self.FILE_EXTENSION):
            AcknowledgementDialogue(
                self.game_root,
                f'Invalid extension for FreeForm Minesweeper board ({PurePath(board_file).suffix}).',
            )
            return
        try:
            with open(board_file, 'w') as board_save_file:
                board_save_file.write('\n'.join(compressed_board))
                board_save_file.write('\n')
        except Exception:
            AcknowledgementDialogue(
                self.game_root,
                'Was not able to save file',
            )

    def place_mines(self, enabled_squares: list[BoardSquare]) -> None:
        """Place mines in the board.

        Args:
            enabled_squares: Enabled squares.
        """
        num_enabled_squares = len(enabled_squares)

        local_difficulty = self.difficulty.get()
        playing_multimine = self.multimine.get()
        multimine_proportion = self.multimine_likelihood.get()

        if playing_multimine:
            local_difficulty += self.multimine_diff_inc.get()
        self.num_mines = min(int(num_enabled_squares * local_difficulty), 999)
        mines_to_place = self.num_mines

        if playing_multimine:
            try:
                spread = (
                    self.mine_spread.get()
                    * (self.num_mines / num_enabled_squares)
                    * (1 - multimine_proportion)
                    / (1 - pow(multimine_proportion, 5))
                )
            except ZeroDivisionError:
                # Limit of (1-p)/(1-p^5) as p -> 1
                # Removable discontinuity
                # Could have instead used 1/(1+p+p^2+p^3+p^4)
                spread = (
                    self.mine_spread.get()
                    * (self.num_mines / num_enabled_squares)
                    * 0.2
                )

            squares_with_mines = sample(
                enabled_squares,
                k=ceil(num_enabled_squares * spread),
            )
        else:
            squares_with_mines = sample(enabled_squares, k=self.num_mines)
        self.squares_to_win = num_enabled_squares - len(squares_with_mines)

        for square in squares_with_mines:
            square.add_mine()
            mines_to_place -= 1

        while mines_to_place > 0:
            batch_size = ceil(len(squares_with_mines) * multimine_proportion)
            squares_with_mines = squares_with_mines[:batch_size]
            for square in squares_with_mines:
                if square.mine_count >= 5:
                    AcknowledgementDialogue(
                        self.game_root,
                        (
                            'Uh oh! Seems there was an error placing mines for this board.\n'
                            'This is a bug, and you can report all the settings that caused it to the GitHub page.\n'
                            'Please include the dimensions, difficulty, difficulty increase, and multimine probability.\n'
                            'In the meantime, try some different settings to play!'
                        ),
                    )
                    self.stop_game()
                    raise RuntimeError('Mine placement went wrong.')
                square.add_mine()
                mines_to_place -= 1
                if mines_to_place == 0:
                    break

    def add_flag(self, square: BoardSquare) -> None:
        """Add a flag to a square.

        Args:
            square: Square being flagged.
        """
        if not square.enabled or not square.covered:
            return
        if square.flag_count < self.max_flags and self.flags_placed < self.num_mines:
            square.add_flag()
            square.image = self.ih.lookup(
                self.board_square_size,
                self.theme,
                self.ih.ImageCategory.BOARD,
                f'flag_{square.flag_count}',
            )
            self.flags_placed += 1
            self.update_flag_counter()

    def remove_flag(self, square: BoardSquare) -> None:
        """Remove a flag from a square.

        Args:
            square: Square being unflagged.
        """
        if not square.enabled or not square.covered:
            return
        if square.flag_count > 0:
            square.remove_flag()
            if square.flag_count == 0:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    'covered',
                )
            else:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    f'flag_{square.flag_count}',
                )
            self.flags_placed -= 1
            self.update_flag_counter()

    def start_game(self) -> None:
        """Exit drawing state and enter sweeping state."""
        self.state = self.State.PAUSE
        squares = self.board_frame.grid_slaves()
        enabled_squares: list[BoardSquare] = []
        for square in squares:
            assert isinstance(square, BoardSquare)
            if square.enabled:
                enabled_squares.append(square)
        if len(enabled_squares) < 9:
            AcknowledgementDialogue(
                self.game_root,
                'Cannot start a game with less than 9 active squares',
            )
            self.stop_game()
            return

        for button in self.get_menu_buttons:
            assert isinstance(button, ttk.Widget)
            if button is self.new_game_button:
                button.state(['!disabled'])
            elif (
                button is self.mode_switch_button
                and self.click_mode.get() != self.ClickMode.FLAGLESS
            ):
                button.state(['!disabled'])
            else:
                button.state(['disabled'])
        self.lock_toolbar()
        self.play_button.grid_remove()
        if not self.classic_ui.get():
            self.stop_button.grid()
        self.clear_history()
        for square in squares:
            assert isinstance(square, BoardSquare)
            if not square.enabled:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    'locked',
                )
            else:
                self.link_squares_neighbours(square)
        self.place_mines(enabled_squares)
        if self.click_mode.get() != self.ClickMode.FLAGLESS:
            self.update_flag_counter()
        self.state = self.State.SWEEP

    def new_game(self) -> None:
        """Start a new game without going back to drawing state."""
        if self.state is self.State.DRAW:
            return
        self.state = self.State.PAUSE
        self.new_game_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'new',
            )
        )
        enabled_squares: list[BoardSquare] = []
        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            if square.enabled:
                enabled_squares.append(square)
                square.reset()
                square.toggle_enable()
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    'covered',
                )
        self.place_mines(enabled_squares)
        self.squares_cleared = 0
        self.flags_placed = 0
        self.time_elapsed = 0.0
        self.reset_timer()
        if self.click_mode.get() != self.ClickMode.FLAGLESS:
            self.update_flag_counter()
        if self.click_mode.get() == self.ClickMode.FLAG:
            self.toggle_click_mode()
        self.state = self.State.SWEEP

    def stop_game(self) -> None:
        """Exit sweeping state and enter drawing state."""
        if self.state is not self.State.PAUSE and self.squares_cleared:
            a = tk.BooleanVar()
            YesNoDialogue(
                self.game_root,
                question='Are you sure you want to stop playing?',
                answer=a,
            )
            if not a.get():
                return
        self.state = self.State.PAUSE
        for button in self.get_menu_buttons:
            assert isinstance(button, ttk.Widget)
            if button in (self.new_game_button, self.mode_switch_button):
                button.state(['disabled'])
            else:
                button.state(['!disabled'])
        self.unlock_toolbar()
        self.stop_button.grid_remove()
        if not self.classic_ui.get():
            self.play_button.grid()
        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            if not square.enabled:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    'unlocked',
                )
            else:
                square.reset()
                square.toggle_enable()
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    'covered',
                )
        self.squares_cleared = 0
        self.flags_placed = 0
        self.squares_to_win = 0
        self.time_elapsed = 0.0
        self.reset_timer()
        self.reset_flag_counter()
        self.new_game_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'new',
            )
        )
        if self.click_mode.get() == self.ClickMode.FLAG:
            self.toggle_click_mode()
        self.state = self.State.DRAW

    def game_won(self) -> None:
        """Game over sequence."""
        self.state = self.State.PAUSE
        self.new_game_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'win',
            )
        )
        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            if square.enabled and square.covered and not square.flag_count:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    f'flag_{square.mine_count}',
                )
        self.reset_flag_counter()
        if not self.prompt_leaderboard_save.get():
            return
        a = tk.BooleanVar()
        YesNoDialogue(
            self.game_root,
            question='Save time to the leaderboard?',
            answer=a,
        )
        if a.get():
            LeaderboardEntryDialogue(
                self.game_root,
                self.compress_board_rle(),
                int(self.time_elapsed),
                self.multimine.get(),
            )

    def game_lost(self) -> None:
        """Game win sequence."""
        self.state = self.State.PAUSE
        self.new_game_button.config(
            image=self.ih.lookup(
                self.ui_square_size,
                self.theme,
                self.ih.ImageCategory.UI,
                'lose',
            )
        )
        for square in self.board_frame.grid_slaves():
            assert isinstance(square, BoardSquare)
            if square.mine_count and not square.flag_count and square.covered:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    f'mine_{square.mine_count}',
                )
            elif square.flag_count and square.flag_count != square.mine_count:
                square.image = self.ih.lookup(
                    self.board_square_size,
                    self.theme,
                    self.ih.ImageCategory.BOARD,
                    f'flag_{square.flag_count}_wrong',
                )

    def mainloop(self) -> None:
        """Run the mainloop to play the game."""
        while self.alive:
            try:
                self.game_root.update_idletasks()
                self.game_root.update()
            except tk.TclError:
                return
            else:
                sleep(self.MAINLOOP_TIME)
                if self.state is self.State.SWEEP and (
                    self.squares_cleared or self.flags_placed
                ):
                    self.time_elapsed = min(
                        round(self.time_elapsed + self.MAINLOOP_TIME, 2),
                        999.0,
                    )
                    if self.time_elapsed.is_integer():
                        try:
                            self.update_timer()
                        except tk.TclError:
                            break


if __name__ == '__main__':
    try:
        FreeFormMinesweeper().mainloop()
    finally:
        Path('README.txt').unlink(missing_ok=True)
