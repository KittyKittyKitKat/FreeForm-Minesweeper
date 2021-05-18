import random
import tkinter as tk
import time

from enum import Enum, auto
from itertools import chain
from tkinter import filedialog
from tkinter import messagebox
from typing import Optional

from PIL import Image, ImageTk


class ClickMode(Enum):
    UNCOVER = auto()
    FLAG = auto()


class GameState(Enum):
    DONE = auto()
    PLAYING = auto()


class Difficulty(Enum):
    EASY = 0.13
    MEDIUM = 0.16
    HARD = 0.207
    EXPERT = 0.25


class Options:
    rows = 30
    cols = 28
    mutlimines = False


class Constants:
    BOARD_SQUARE_SIZE = 32
    SEGMENT_HEIGHT = 46
    SEGMENT_WIDTH = 26
    PADDING_DIST = 5
    WINDOW_WIDTH = BOARD_SQUARE_SIZE * Options.cols
    BOARD_HEIGHT = BOARD_SQUARE_SIZE * Options.rows
    BACKGROUND_COLOUR = '#c0c0c0'
    DEFAULT_COLOUR = '#d9d9d9'
    FONT = ('MINE-SWEEPER', 7, 'normal')
    MAINLOOP_TIME = 0.01
    LOCKED_BLACK_SQUARE = Image.new('RGBA', size=(32, 32), color=(0, 0, 0))
    UNLOCKED_BLACK_SQUARE = Image.new('RGBA', size=(32, 32), color=(0, 0, 0))
    FILE_TYPE = (('FreeForm Minesweeper Board', '*.ffmnswpr'),)

    @staticmethod
    def init_board_images() -> None:
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
        EXTENDED_BOARD_IMAGES = []
        with Image.open('assets/board_sheet.png') as board_sheet:
            x, y = board_sheet.size
            for i in range(0, y, Constants.BOARD_SQUARE_SIZE):
                for j in range(0, x, Constants.BOARD_SQUARE_SIZE):
                    im = board_sheet.crop((j, i, j + Constants.BOARD_SQUARE_SIZE, i + Constants.BOARD_SQUARE_SIZE))
                    im2 = ImageTk.PhotoImage(im)
                    EXTENDED_BOARD_IMAGES.append(im2)
        setattr(Constants, 'BOARD_IMAGES', EXTENDED_BOARD_IMAGES)


class GameControl:
    click_mode = ClickMode.UNCOVER
    game_state = GameState.PLAYING
    difficulty = Difficulty.EASY
    num_mines = None
    squares_to_win = None
    squares_uncovered = 0
    flags_placed = 0
    grace_rule = True
    seconds_elpased = 0
    on_hold = True
    drag_mode = True

    @staticmethod
    def check_win() -> None:
        if GameControl.squares_uncovered == GameControl.squares_to_win:
            WindowControl.reset_button.config(im=Constants.BOARD_IMAGES[16])
            GameControl.game_state = GameState.DONE
            GameControl.flags_placed = GameControl.num_mines
            WindowControl.update_flag_counter()
            for square in WindowControl.board_frame.grid_slaves():
                if square.enabled and not square.uncovered:
                    square.config(im=Constants.BOARD_IMAGES[11])

    @staticmethod
    def has_lost() -> None:
        WindowControl.reset_button.config(im=Constants.BOARD_IMAGES[15])
        GameControl.game_state = GameState.DONE
        for square in WindowControl.board_frame.grid_slaves():
            if square.enabled and not square.uncovered and not square.flagged and square.value == -1:
                square.config(im=Constants.BOARD_IMAGES[9])
            if square.flagged and square.value != -1:
                square.config(im=Constants.BOARD_IMAGES[12])

    @staticmethod
    def play_game() -> None:
        WindowControl.root.unbind('<Control-i>')
        num_squares = sum([1 if sq.enabled else 0 for sq in WindowControl.board_frame.grid_slaves()])
        GameControl.num_mines = min(int(num_squares * GameControl.difficulty.value), 999)
        GameControl.squares_to_win = num_squares - GameControl.num_mines
        GameControl.squares_uncovered = 0
        GameControl.flags_placed = 0
        GameControl.seconds_elpased = 0
        GameControl.click_mode = ClickMode.UNCOVER
        GameControl.on_hold = False

        WindowControl.update_flag_counter()
        squares = WindowControl.board_frame.grid_slaves()
        mines_placed = 0
        while mines_placed < GameControl.num_mines:
            sq = random.choice(squares)
            if not sq.value and sq.enabled:
                sq.value = -1
                mines_placed += 1

        for sq in squares:
            sq.lock()
            sq.link_to_neighbours()
            sq.unbind('<B1-Motion>')
            sq.bind('<Button-1>', lambda event, square=sq: square.uncover())
            sq.bind('<Button-3>', lambda event, square=sq: square.flag())
            sq.bind('<Double-Button-1>', lambda event, square=sq: square.chord())

        WindowControl.reset_button.bind('<ButtonPress-1>', lambda event: WindowControl.reset_button.config(im=Constants.BOARD_IMAGES[14]))
        WindowControl.reset_button.bind('<ButtonRelease-1>', lambda event: GameControl.reset_game())
        WindowControl.mode_switch_button.bind('<ButtonPress-1>', lambda event: GameControl.swtich_mode())
        options = WindowControl.play_button.grid_info()
        WindowControl.play_button.grid_remove()
        WindowControl.stop_button.grid(**options)
        btns = chain(
            WindowControl.diff_frame.grid_slaves(),
            WindowControl.controls_frame.grid_slaves(),
            WindowControl.presets_frame.grid_slaves()
        )
        for btn in btns:
            if isinstance(btn, tk.Button):
                btn.config(state='disabled')

        GameControl.game_state = GameState.PLAYING

    @staticmethod
    def reset_game() -> None:
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
        GameControl.on_hold = True
        WindowControl.root.bind('<Control-i>', lambda event: GameControl.invert_board())
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
            WindowControl.presets_frame.grid_slaves()
        )
        for btn in btns:
            if isinstance(btn, tk.Button):
                btn.config(state='normal')
        for sq in WindowControl.board_frame.grid_slaves():
            sq.unlock()
            sq.bind('<Button-1>', lambda event, square=sq: square.toggle_enable())
            sq.bind('<B1-Motion>', lambda event, square=sq: WindowControl.drag_enable_toggle(event, square))
            sq.unbind('<Double-Button-1>')

    @staticmethod
    def change_difficulty(difficulty: Difficulty, btn_pressed: tk.Button) -> None:
        GameControl.difficulty = difficulty
        for diff_btn in WindowControl.diff_frame.grid_slaves():
            if isinstance(diff_btn, tk.Button):
                diff_btn.config(relief='raised', bg=Constants.DEFAULT_COLOUR)
        btn_pressed.config(relief='sunken', bg=Constants.BACKGROUND_COLOUR)

    @staticmethod
    def fill_board() -> None:
        for sq in WindowControl.board_frame.grid_slaves():
            if not sq.enabled:
                sq.toggle_enable()

    @staticmethod
    def clear_board() -> None:
        for sq in WindowControl.board_frame.grid_slaves():
            if sq.enabled:
                sq.toggle_enable()

    @staticmethod
    def swtich_mode() -> None:
        if GameControl.click_mode is ClickMode.UNCOVER:
            GameControl.click_mode = ClickMode.FLAG
            WindowControl.mode_switch_button.config(im=Constants.BOARD_IMAGES[18])
        else:
            GameControl.click_mode = ClickMode.UNCOVER
            WindowControl.mode_switch_button.config(im=Constants.BOARD_IMAGES[17])

    @staticmethod
    def save_board() -> None:
        # Commented to hell and back in case I ever forget my logic here
        # Keep track of the leftmost enabled sqaure. Set to the right side of the field
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
            # Otherwise, if the bit row has 1 but is in the content of the board
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
        # Save to a file
        board_file = filedialog.asksaveasfilename(initialdir='../..', title='Save Board', filetypes=Constants.FILE_TYPE)
        try:
            with open(board_file, 'w') as board_save_file:
                board_save_file.write('\n'.join(board_bits))
                board_save_file.write('\n')
        except Exception:
            messagebox.showerror(title='Saving Error', message='Was not able to save the file.')

    @staticmethod
    def load_board(filename: Optional[str] = None) -> None:
        board_file = filename or filedialog.askopenfilename(initialdir='../..', title='Open Board', filetypes=Constants.FILE_TYPE)
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
        for sq in WindowControl.board_frame.grid_slaves():
            sq.toggle_enable()


class BoardSquare(tk.Label):
    def __init__(self, master: tk.Widget, size: int, tk_image: tk.PhotoImage) -> None:
        super().__init__(master, height=size, width=size, im=tk_image, bd=0)
        self.master = master
        self.image = tk_image
        self.uncovered = False
        self.flagged = False
        self.enabled = True
        self.value = 0
        self.directions = ('nw', 'n', 'ne', 'w', 'e', 'sw', 's', 'se')
        self.neighbours = dict.fromkeys(self.directions)

    def link_to_neighbours(self) -> None:
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

    def uncover(self, override_click_mode: bool = False) -> None:
        if GameControl.click_mode is ClickMode.FLAG and not override_click_mode:
            self.flag()
        if not self.enabled or GameControl.game_state is GameState.DONE:
            return
        if not self.uncovered and not self.flagged:
            if self.value != -1:
                self.uncovered = True
                GameControl.squares_uncovered += 1
                mines_around = 0
                for neighbour in self.neighbours.values():
                    if neighbour is not None and neighbour.value == -1:
                        mines_around += 1
                self.value = mines_around
                self.image = Constants.BOARD_IMAGES[self.value]
                self.config(im=self.image)
                if not self.value:
                    for neighbour in self.neighbours.values():
                        if neighbour is not None and not neighbour.flagged:
                            neighbour.uncover(override_click_mode=override_click_mode)
            else:
                if GameControl.grace_rule and GameControl.squares_uncovered == 0:
                    GameControl.reset_game()
                    return
                if GameControl.game_state is GameState.PLAYING:
                    GameControl.has_lost()
                self.image = Constants.BOARD_IMAGES[10]
                self.config(im=self.image)
        GameControl.check_win()

    def flag(self) -> None:
        if not self.enabled or self.uncovered or GameControl.game_state is GameState.DONE:
            return
        if not self.flagged and GameControl.flags_placed < GameControl.num_mines:
            self.flagged = not self.flagged
            self.image = Constants.BOARD_IMAGES[11]
            self.config(im=self.image)
            GameControl.flags_placed += 1
        elif self.flagged:
            self.flagged = not self.flagged
            self.image = Constants.BOARD_IMAGES[20]
            self.config(im=self.image)
            GameControl.flags_placed -= 1
        WindowControl.update_flag_counter()

    def chord(self) -> None:
        if not self.enabled or GameControl.game_state is GameState.DONE:
            return
        if self.uncovered and not self.flagged:
            flags_around = 0
            for neighbour in self.neighbours.values():
                if neighbour is not None and neighbour.flagged:
                    flags_around += 1
            if flags_around == self.value:
                for neighbour in self.neighbours.values():
                    if neighbour is not None and not neighbour.flagged:
                        neighbour.uncover(override_click_mode=True)

    def toggle_enable(self) -> None:
        if self.enabled:
            self.config(im=Constants.UNLOCKED_BLACK_SQUARE)
        else:
            self.config(im=self.image)
        self.enabled = not self.enabled

    def lock(self) -> None:
        if not self.enabled:
            self.config(im=Constants.LOCKED_BLACK_SQUARE)

    def unlock(self) -> None:
        if not self.enabled:
            self.config(im=Constants.UNLOCKED_BLACK_SQUARE)

    def reset(self) -> None:
        self.image = Constants.BOARD_IMAGES[20]
        self.config(im=self.image)
        self.uncovered = False
        self.flagged = False
        self.enabled = True
        self.value = 0
        self.neighbours = dict.fromkeys(self.directions)


class WindowControl:
    root = tk.Tk()
    main_frame = tk.Frame(
        root, width=Constants.WINDOW_WIDTH,
        height=Constants.BOARD_HEIGHT + Constants.SEGMENT_HEIGHT + 4 * Constants.PADDING_DIST, bg='black'
    )
    menu_frame = tk.Frame(
        main_frame, width=Constants.WINDOW_WIDTH, height=Constants.SEGMENT_HEIGHT + 4 * Constants.PADDING_DIST,
        bg=Constants.BACKGROUND_COLOUR
    )
    board_frame = tk.Frame(
        main_frame, width=Constants.WINDOW_WIDTH, height=Constants.BOARD_HEIGHT,
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
    play_button = tk.Button(mswpr_frame, text='Play', font=Constants.FONT, width=5, command=GameControl.play_game)
    stop_button = tk.Button(mswpr_frame, text='Stop', font=Constants.FONT, width=5, command=GameControl.stop_game)

    @staticmethod
    def init_window() -> None:
        WindowControl.root.resizable(0, 0)
        WindowControl.root.title('FreeForm Minesweeper')
        WindowControl.root.bind('<Control-i>', lambda event: GameControl.invert_board())
        WindowControl.main_frame.pack_propagate(0)
        WindowControl.menu_frame.grid_propagate(0)
        WindowControl.board_frame.grid_propagate(0)
        for i in range(8):
            WindowControl.menu_frame.grid_columnconfigure(i, weight=1)
        WindowControl.menu_frame.pack()
        WindowControl.board_frame.pack()
        WindowControl.main_frame.pack()

    @staticmethod
    def init_board() -> None:
        for i in range(Options.rows):
            WindowControl.board_frame.grid_rowconfigure(i, minsize=Constants.BOARD_SQUARE_SIZE)
        for i in range(Options.cols):
            WindowControl.board_frame.grid_columnconfigure(i, minsize=Constants.BOARD_SQUARE_SIZE)
        for x in range(Options.rows):
            for y in range(Options.cols):
                sq = BoardSquare(WindowControl.board_frame, Constants.BOARD_SQUARE_SIZE, Constants.BOARD_IMAGES[20])
                sq.toggle_enable()
                sq.bind('<Button-1>', lambda event, square=sq: square.toggle_enable())
                sq.bind('<B1-Motion>', lambda event, square=sq: WindowControl.drag_enable_toggle(event, square))
                sq.grid(row=x, column=y)

    @staticmethod
    def init_menu() -> None:
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
        preset_easy.grid(row=0, column=0)
        preset_medium.grid(row=0, column=1)
        preset_hard.grid(row=1, column=0)
        preset_expert.grid(row=1, column=1)
        WindowControl.presets_frame.grid(row=0, column=0)

        flag_left = tk.Label(WindowControl.flags_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        flag_mid = tk.Label(WindowControl.flags_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        flag_right = tk.Label(WindowControl.flags_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        flag_left.grid(row=0, column=0)
        flag_mid.grid(row=0, column=1)
        flag_right.grid(row=0, column=2)
        WindowControl.flags_frame.grid(row=0, column=1)

        WindowControl.mode_switch_button.config(im=Constants.BOARD_IMAGES[17])
        WindowControl.reset_button.config(im=Constants.BOARD_IMAGES[13])
        WindowControl.mode_switch_button.grid(row=0, column=0, pady=2)
        WindowControl.reset_button.grid(row=0, column=1)
        WindowControl.play_button.grid(row=1, column=0, columnspan=2)
        WindowControl.mswpr_frame.grid(row=0, column=2)

        timer_left = tk.Label(WindowControl.timer_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        timer_mid = tk.Label(WindowControl.timer_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        timer_right = tk.Label(WindowControl.timer_frame, width=Constants.SEGMENT_WIDTH, height=Constants.SEGMENT_HEIGHT, bd=0, im=Constants.SEVSEG_IMAGES[0])
        timer_left.grid(row=0, column=0)
        timer_mid.grid(row=0, column=1)
        timer_right.grid(row=0, column=2)
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
        diff_label.grid(row=0, column=1, columnspan=4)
        diff_1.grid(row=1, column=1)
        diff_2.grid(row=1, column=2)
        diff_3.grid(row=1, column=3)
        diff_4.grid(row=1, column=4)
        WindowControl.diff_frame.grid(row=0, column=4)

        fill_button = tk.Button(WindowControl.controls_frame, text='Fill', font=Constants.FONT, width=5, command=GameControl.fill_board)
        clear_button = tk.Button(WindowControl.controls_frame, text='Clear', font=Constants.FONT, width=5, command=GameControl.clear_board)
        save_board_button = tk.Button(WindowControl.controls_frame, text='Save', font=Constants.FONT, width=5, command=lambda: GameControl.save_board())
        load_board_button = tk.Button(WindowControl.controls_frame, text='Load', font=Constants.FONT, width=5, command=lambda: GameControl.load_board())
        fill_button.grid(row=0, column=0)
        clear_button.grid(row=1, column=0)
        save_board_button.grid(row=0, column=1, padx=Constants.PADDING_DIST)
        load_board_button.grid(row=1, column=1)
        WindowControl.controls_frame.grid(row=0, column=5)

    @staticmethod
    def update_timer() -> None:
        if (GameControl.squares_uncovered or GameControl.flags_placed) and GameControl.game_state is GameState.PLAYING and not GameControl.on_hold:
            seconds = list(str(int(GameControl.seconds_elpased)).zfill(3))
            for number in WindowControl.timer_frame.grid_slaves():
                number.config(im=Constants.SEVSEG_IMAGES[int(seconds.pop())])

    @staticmethod
    def reset_timer() -> None:
        for number in WindowControl.timer_frame.grid_slaves():
            number.config(im=Constants.SEVSEG_IMAGES[0])

    @staticmethod
    def update_flag_counter() -> None:
        flags = GameControl.num_mines - GameControl.flags_placed
        value_container = list(str(flags).zfill(3))
        for number in WindowControl.flags_frame.grid_slaves():
            number.config(im=Constants.SEVSEG_IMAGES[int(value_container.pop())])

    @staticmethod
    def reset_flag_counter() -> None:
        for number in WindowControl.flags_frame.grid_slaves():
            number.config(im=Constants.SEVSEG_IMAGES[0])

    @staticmethod
    def drag_enable_toggle(event: tk.EventType.Motion, initial_square: BoardSquare) -> None:
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


def main() -> None:
    WindowControl.init_window()
    Constants.init_board_images()
    Constants.init_sevseg_images()
    Constants.init_extended_board_images()
    Constants.DEFAULT_COLOUR = WindowControl.root.cget('bg')
    WindowControl.init_menu()
    WindowControl.diff_frame.grid_slaves()[-2].invoke()
    WindowControl.init_board()
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
