# Copyright © Simon Harris-Palmer 2023. All rights reserved.

import json
import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from datetime import date
from tkinter.simpledialog import Dialog
from typing import Literal, TypeAlias, TypedDict


class AcknowledgementDialogue(Dialog):
    """Message dialogue with an okay button."""

    def __init__(
        self,
        parent: tk.Toplevel,
        message: str,
        title: str = 'FreeForm Minesweeper',
    ) -> None:
        """Initialize the dialogue.

        Args:
            parent: Parent of the modal window.
            message: Message displayed in the modal window.
            title: Title of the modal window. Defaults to 'FreeForm Minesweeper'.
        """
        self.message = message
        super().__init__(parent, title)

    def body(self, parent: tk.Frame) -> tk.Frame:
        """Internal method."""
        self.resizable(False, False)
        self['bg'] = ttk.Style().configure('FFMS.TFrame')['background']
        message_label = ttk.Label(
            parent,
            text=self.message,
            style='FFMS.TLabel',
        )
        message_label.pack()
        return parent

    def buttonbox(self) -> None:
        """Internal method."""
        box = ttk.Frame(self, style='FFMS.TFrame')
        w = ttk.Button(
            box,
            text='OK',
            width=10,
            command=self.cancel,
            default=tk.ACTIVE,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind('<Return>', self.cancel)
        self.bind('<Escape>', self.cancel)
        box.pack()


class AcknowledgementWithLinkDialogue(Dialog):
    """Message dialogue with an okay button."""

    def __init__(
        self,
        parent: tk.Toplevel,
        message: str,
        link: tuple[str, str],
        title: str = 'FreeForm Minesweeper',
    ) -> None:
        """Initialize the dialogue.

        Args:
            parent: Parent of the modal window.
            message: Message displayed in the modal window.
            link: 2-tuple. First element is link text, second is link URL.
            title: Title of the modal window. Defaults to 'FreeForm Minesweeper'.
        """
        self.message = message
        self.link = link
        super().__init__(parent, title)

    def body(self, parent: tk.Frame) -> tk.Frame:
        """Internal method."""
        self.resizable(False, False)
        background = ttk.Style().configure('FFMS.TFrame')['background']
        self['bg'] = background
        parent['bg'] = background

        message_label = ttk.Label(
            parent,
            text=self.message,
            style='FFMS.TLabel',
        )
        message_label.pack()
        link_label = ttk.Label(
            parent, text=self.link[0], style='Link.FFMS.TLabel', cursor='hand2'
        )
        link_label.bind('<Button-1>', lambda *_: webbrowser.open_new_tab(self.link[1]))
        link_label.pack()
        return parent

    def buttonbox(self) -> None:
        """Internal method."""
        box = ttk.Frame(self, style='FFMS.TFrame')
        w = ttk.Button(
            box,
            text='Close',
            width=10,
            command=self.cancel,
            default=tk.ACTIVE,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind('<Return>', self.cancel)
        self.bind('<Escape>', self.cancel)
        box.pack()


class YesNoDialogue(Dialog):
    """Question Dialogue with Yes/No buttons."""

    def __init__(
        self,
        parent: tk.Toplevel,
        title: str = 'FreeForm Minesweeper',
        question: str = '',
        answer: tk.BooleanVar | None = None,
    ) -> None:
        """Initialize the dialogue.

        Args:
            parent: Parent of the modal window.
            title: Title of the modal window. Defaults to 'FreeForm Minesweeper'.
            question: Question displayed in the modal window. Defaults to ''.
            answer: Result of button interaction. Defaults to None.
        """
        self.question = question
        self.answer = answer
        super().__init__(parent, title)

    def body(self, parent: tk.Frame) -> tk.Frame:
        """Internal method."""
        self.resizable(False, False)
        self['bg'] = ttk.Style().configure('FFMS.TFrame')['background']
        question_label = ttk.Label(
            parent,
            text=self.question,
            style='FFMS.TLabel',
        )
        question_label.pack()
        return parent

    def buttonbox(self) -> None:
        """Internal method."""
        box = ttk.Frame(self, style='FFMS.TFrame')
        w = ttk.Button(
            box,
            text='Yes',
            width=10,
            command=self.ok,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(
            box,
            text='No',
            width=10,
            command=self.cancel,
            default=tk.ACTIVE,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)
        box.pack()

    def ok(self, event: tk.Event | None = None) -> None:
        """Internal method."""
        if self.answer:
            self.answer.set(True)
        super().ok()

    def cancel(self, event: tk.Event | None = None) -> None:
        """Internal method."""
        if self.answer and not self.answer.get():
            self.answer.set(False)
        super().cancel()


class SettingsDialogue(Dialog):
    """Extra game settings dialogue."""

    def __init__(
        self,
        parent: tk.Toplevel,
        settings: dict[str, tuple[float, float, float, tk.Variable]],
    ) -> None:
        """Initialize the dialogue.

        Args:
            parent: Parent of the modal window.
            settings: Description, parameters, and variable for sliders.
        """
        self.settings = settings
        self.local_mapping: dict[tk.Scale, tk.Variable] = {}
        super().__init__(parent, 'FreeForm Minesweeper Settings')

    def body(self, parent: tk.Frame) -> tk.Frame:
        """Internal method."""
        self.resizable(False, False)
        background = ttk.Style().configure('FFMS.TFrame')['background']
        font = ttk.Style().configure('FFMS.TLabel')['font']
        self['bg'] = background
        parent['bg'] = background
        r = 0
        for desc, t in self.settings.items():
            from_, to, res, var = t
            s = tk.Scale(
                parent,
                orient=tk.HORIZONTAL,
                font=font,
                bg=background,
                resolution=res,
                from_=from_,
                to=to,
                length=300,
                bd=0,
                label=desc,
                relief=tk.FLAT,
                highlightthickness=0,
                takefocus=False,
            )
            s.set(var.get())
            s.grid(row=r, column=1)
            r += 1
            self.local_mapping[s] = var
        return parent

    def buttonbox(self) -> None:
        """Internal method."""
        box = ttk.Frame(self, style='FFMS.TFrame')
        w = ttk.Button(
            box,
            text='Cancel',
            width=10,
            command=self.cancel,
            default=tk.ACTIVE,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(
            box,
            text='Apply',
            width=10,
            command=self.ok,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)
        box.pack()

    def apply(self) -> None:
        """Apply settings from dialogue to passed in variables."""
        for scale, var in self.local_mapping.items():
            if var.get() != scale.get():
                var.set(scale.get())


_LEADERBOARD_FILENAME = 'leaderboard.json'
TimeEntry = TypedDict('TimeEntry', {'Time': int, 'Date': str})
BoardEntry = TypedDict(
    'BoardEntry',
    {'Board': str, 'Mode': Literal['MULTI', 'NORMAL'], 'Entries': list[TimeEntry]},
)
PlayerName: TypeAlias = str
BoardName: TypeAlias = str
LeaderboardJSON: TypeAlias = dict[PlayerName, dict[BoardName, BoardEntry]]


class LeaderboardRenameDialog(Dialog):
    """Entry dialogue to rename players and boards in the leaderboard."""

    def __init__(
        self,
        parent: tk.Toplevel,
        leaderboard: LeaderboardJSON,
        attr_renaming: Literal['board', 'player'],
        old_player_name: str,
        old_board_name: str,
    ) -> None:
        """Initialize the dialogue.

        Args:
            parent: Parent of the modal window.
            leaderboard: Current leaderboard
            attr_renaming: The attribute of the leaderboard being renamed.
            old_player_name: The old player name.
            old_board_name: The old board name.
        """
        self.leaderboard = leaderboard
        self.entry_var = tk.StringVar()
        self.attr_renaming: Literal['board', 'player'] = attr_renaming
        self.old_player_name = old_player_name
        self.old_board_name = old_board_name.split('@')[-1]
        if self.attr_renaming == 'player':
            self.entry_var.set(self.old_player_name)
        elif self.attr_renaming == 'board':
            self.entry_var.set(self.old_board_name)
        self.entry_var.trace_add(
            'write',
            lambda *_: self.entry_var.set(self.entry_var.get().upper()),
        )
        super().__init__(parent, 'FreeForm Minesweeper Leaderboard')

    def body(self, parent: tk.Frame) -> ttk.Entry:
        """Internal method."""
        self.resizable(False, False)
        background = ttk.Style().configure('FFMS.TFrame')['background']
        font = ttk.Style().configure('FFMS.TLabel')['font']
        self['bg'] = background
        parent['bg'] = background
        label = ttk.Label(
            parent,
            text=f'Enter a new {self.attr_renaming} name [A-Z]',
            style='FFMS.TLabel',
        )
        self.entry = ttk.Entry(
            parent,
            exportselection=False,
            textvariable=self.entry_var,
            font=font,
            style='FFMS.TEntry',
        )
        self.entry.icursor(tk.END)
        self.entry.bind(
            '<Control-KeyRelease-a>',
            lambda event: self.entry.select_range(0, tk.END),
        )
        label.grid(row=0, column=0)
        self.entry.grid(row=1, column=0)
        return self.entry

    def buttonbox(self) -> None:
        """Internal method."""
        box = ttk.Frame(self, style='FFMS.TFrame')
        w = ttk.Button(
            box,
            text='Cancel',
            width=10,
            command=self.cancel,
            default=tk.ACTIVE,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(
            box,
            text='Submit',
            width=10,
            command=self.ok,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)
        box.pack()

    def validate(self) -> bool:
        """Internal method."""
        name = self.entry_var.get()
        if not name:
            AcknowledgementDialogue(
                parent=self,
                title='Rename in Leaderboard Error',
                message='Names entered cannot be blank',
            )
            return False
        if not name.isalpha():
            AcknowledgementDialogue(
                parent=self,
                title='Rename in Leaderboard Error',
                message='Names entered can only contain letters [A-Z]',
            )
            return False
        if self.attr_renaming == 'player':
            if name != self.old_player_name and name in self.leaderboard:
                AcknowledgementDialogue(
                    parent=self,
                    title='Rename in Leaderboard Error',
                    message='Player name already exists',
                )
                return False
            elif name == self.old_player_name:
                return True
        elif self.attr_renaming == 'board':
            if (
                name != self.old_board_name
                and name in self.leaderboard[self.old_player_name]
            ):
                AcknowledgementDialogue(
                    parent=self,
                    title='Rename in Leaderboard Error',
                    message='Board name already exists for player.',
                )
                return False
            elif name == self.old_board_name:
                return True
        return True

    def apply(self) -> None:
        """Internal method."""
        if self.attr_renaming == 'player':
            if self.entry_var.get() == self.old_player_name:
                return
            player_boards = self.leaderboard[self.old_player_name]
            self.leaderboard[self.entry_var.get()] = player_boards
            self.leaderboard.pop(self.old_player_name)
        elif self.attr_renaming == 'board':
            if self.entry_var.get() == self.old_board_name:
                return
            board_data = self.leaderboard[self.old_player_name][self.old_board_name]
            self.leaderboard[self.old_player_name][self.entry_var.get()] = board_data
            self.leaderboard[self.old_player_name].pop(self.old_board_name)


class LeaderboardEntryDialogue(Dialog):
    """Entry dialogue that updates leaderboard database."""

    def __init__(
        self,
        parent: tk.Toplevel,
        board_id: str,
        time_elapsed: int,
        played_multimine: bool,
    ) -> None:
        """Initialize the dialogue.

        Args:
            parent: Parent of the modal window.
            board_id: ID of the board played on.
            time_elapsed: Time spent playing on the board.
            played_multimine: Board was played with multimine mode.
        """
        self.board_id = board_id
        self.time_elapsed = time_elapsed
        self.played_multimine = played_multimine

        self.player_var = tk.StringVar()
        self.board_var = tk.StringVar()
        self.leaderboard: LeaderboardJSON = {}
        self.override_same_name = False
        try:
            with open(_LEADERBOARD_FILENAME, mode='r') as fp:
                self.leaderboard = json.load(fp)
        except FileNotFoundError:
            fp = open(_LEADERBOARD_FILENAME, mode='x')
            fp.close()
        self.player_var.trace_add(
            'write',
            lambda *_: self.player_var.set(self.player_var.get().upper()),
        )
        self.board_var.trace_add(
            'write',
            lambda *_: self.board_var.set(self.board_var.get().upper()),
        )
        super().__init__(parent, 'FreeForm Minesweeper Leaderboard')

    def body(self, parent: tk.Frame) -> ttk.Entry:
        """Internal method."""
        self.resizable(False, False)
        background = ttk.Style().configure('FFMS.TFrame')['background']
        font = ttk.Style().configure('FFMS.TLabel')['font']
        self['bg'] = background
        parent['bg'] = background
        time_label = ttk.Label(
            parent,
            text=f'Your time was: {int(self.time_elapsed)} seconds.',
            style='FFMS.TLabel',
        )
        player_label = ttk.Label(
            parent,
            text='Player Name',
            style='FFMS.TLabel',
        )
        player_entry = ttk.Entry(
            parent,
            exportselection=False,
            textvariable=self.player_var,
            font=font,
            style='FFMS.TEntry',
        )
        name_label = ttk.Label(
            parent,
            text='Name This Board',
            style='FFMS.TLabel',
        )
        self.name_entry = ttk.Entry(
            parent,
            exportselection=False,
            textvariable=self.board_var,
            font=font,
            style='FFMS.TEntry',
        )
        if self.played_multimine:
            multimine_label = ttk.Label(
                parent,
                text='You played on multimine mode',
                style='FFMS.TLabel',
            )
            multimine_label.grid(row=5, column=0, pady=6)
        player_entry.bind(
            '<Control-KeyRelease-a>',
            lambda event: player_entry.select_range(0, tk.END),
        )
        self.name_entry.bind(
            '<Control-KeyRelease-a>',
            lambda *_: self.name_entry.select_range(0, tk.END),
        )
        time_label.grid(row=0, column=0, pady=6)
        player_label.grid(row=1, column=0)
        player_entry.grid(row=2, column=0)
        name_label.grid(row=3, column=0)
        self.name_entry.grid(row=4, column=0)
        self.player_var.trace_add('write', lambda *_: self.autofill_board_name())
        return player_entry

    def buttonbox(self) -> None:
        """Internal method."""
        box = ttk.Frame(self, style='FFMS.TFrame')
        w = ttk.Button(
            box,
            text='Cancel',
            width=10,
            command=self.cancel,
            default=tk.ACTIVE,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(
            box,
            text='Submit',
            width=10,
            command=self.ok,
            style='FFMS.Toolbutton',
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)
        box.pack()

    def validate(self) -> bool:
        """Internal method."""
        board_name = self.board_var.get()
        player_name = self.player_var.get()
        if not board_name or not player_name:
            AcknowledgementDialogue(
                parent=self,
                title='Save to Leaderboard Error',
                message='Names entered cannot be blank',
            )
            return False
        if not (board_name.isalpha() and player_name.isalpha()):
            AcknowledgementDialogue(
                parent=self,
                title='Save to Leaderboard Error',
                message='Names entered can only contain letters [A-Z]',
            )
            return False
        if not self.override_same_name:
            for p_name, b_entry in self.leaderboard.items():
                if p_name == player_name and board_name in b_entry:
                    AcknowledgementDialogue(
                        parent=self,
                        title='FFMS Leaderboard Error',
                        message='Board names must be unique for a player',
                    )
                    return False
        return True

    def apply(self) -> None:
        """Internal method."""
        player_name = self.player_var.get().upper()
        board_name = self.board_var.get().upper()
        if player_name not in self.leaderboard:
            self.leaderboard[player_name] = {}
        if board_name not in self.leaderboard[player_name]:
            self.leaderboard[player_name][board_name] = {
                'Board': self.board_id,
                'Mode': 'MULTI' if self.played_multimine else 'NORMAL',
                'Entries': [],
            }
        self.leaderboard[player_name][board_name]['Entries'].append(
            {'Time': self.time_elapsed, 'Date': date.today().strftime('%m/%d/%y')}
        )
        with open(_LEADERBOARD_FILENAME, mode='w') as fp:
            json.dump(self.leaderboard, fp, indent=4)

    def autofill_board_name(self) -> None:
        """Autofill the name in the board entry based on the current board and player."""
        p_name = self.player_var.get().upper()
        mode = 'MULTI' if self.played_multimine else 'NORMAL'
        if b_dict := self.leaderboard.get(p_name, None):
            for b_name, b_entry in b_dict.items():
                if b_entry['Board'] == self.board_id and b_entry['Mode'] == mode:
                    self.board_var.set(b_name)
                    self.name_entry.state([tk.DISABLED])
                    self.override_same_name = True
                    return
        elif self.name_entry.state() == tk.DISABLED:
            self.name_entry.state(['!' + tk.DISABLED])
            self.name_entry.delete(0, tk.END)


class LeaderboardViewDialogue(Dialog):
    """Treeview dialogue to access leaderboard database."""

    def __init__(self, parent: tk.Toplevel) -> None:
        """Initialize the dialogue.

        Args:
            parent: Parent of the modal window.
        """
        self.leaderboard: LeaderboardJSON = {}
        self.images: set[tk.PhotoImage] = set()
        style = ttk.Style()
        self.menu_bg = style.configure('FFMS.TMenu')['background']
        self.menu_fg = style.configure('FFMS.TMenu')['foreground']
        self.menu_abg = style.configure('FFMS.TMenu')['activebackground']
        self.menu_afg = style.configure('FFMS.TMenu')['activeforeground']
        try:
            with open(_LEADERBOARD_FILENAME, mode='r') as fp:
                self.leaderboard = json.load(fp)
        except FileNotFoundError:
            AcknowledgementDialogue(parent, message='No leaderboard was found.')
            return
        super().__init__(parent, title='FreeForm Minesweeper Leaderboard')

    def body(self, parent: tk.Frame) -> tk.Frame:
        """Internal method."""
        self.resizable(False, False)
        background = ttk.Style().configure('FFMS.TFrame')['background']
        self['bg'] = background
        parent['bg'] = background
        self.tree = ttk.Treeview(
            parent,
            columns=('date',),
            selectmode='none',
            style='FFMS.Treeview',
            takefocus=False,
            show='tree',
        )
        self.tree.column('#0', width=300, minwidth=64, stretch=True)
        self.load_tree()
        self.tree.tag_bind('player', '<Button-3>', self.player_binding)
        self.tree.tag_bind('board', '<Button-3>', self.board_binding)
        self.tree.tag_bind('time', '<Button-3>', self.time_binding)
        self.tree.grid(row=0, column=0)
        scrollbar = ttk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )
        # Mypy does not like this configure call
        self.tree.configure(yscroll=scrollbar.set)  # type: ignore
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        return parent

    def buttonbox(self) -> None:
        """Internal method."""
        return None

    def load_tree(self) -> None:
        """Load the leaderboard into the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p_name, b_entry in sorted(self.leaderboard.items()):
            self.tree.insert(
                '',
                tk.END,
                iid=p_name,
                text=f'Player: {p_name.title()}',
                tags='player',
            )
            for b_name, entry in sorted(b_entry.items()):
                self.tree.insert(
                    p_name,
                    tk.END,
                    iid=f'{p_name}@{b_name}',
                    text=f'  Board: {b_name.title()}',
                    image=self.generate_board_thumbnail(entry['Board']),
                    values=(
                        'MultiMine Mode' if entry['Mode'] == 'MULTI' else 'Normal Mode',
                    ),
                    tags='board',
                )
                for time in sorted(entry['Entries'], key=lambda e: e['Time']):
                    self.tree.insert(
                        f'{p_name}@{b_name}',
                        tk.END,
                        text=f'{time["Time"]} seconds',
                        values=(time['Date'],),
                        tags='time',
                    )

    def generate_board_thumbnail(self, compressed_board_id: str) -> tk.PhotoImage:
        """Generate a black and white image representing a board.

        Args:
            compressed_board_id: List of binary strings representing the board.

        Returns:
            Image generated from board.
            Enabled squares are displayed as white, and unenabled as black.
        """
        board_bits = self.decompress_board(compressed_board_id)
        max_dim_y = len(max(board_bits, key=len))
        max_dim_x = len(board_bits)
        size = 64
        padding_y = (size - max_dim_y) // 2
        padding_x = (size - max_dim_x) // 2
        thumbnail = tk.PhotoImage(height=size, width=size)
        # Valid call but no function signature
        thumbnail.put('black', to=(0, 0, size, size))  # type: ignore
        for x, bit_row in enumerate(board_bits):
            for y, bit in enumerate(bit_row):
                if int(bit):
                    thumbnail.put('white', to=(y + padding_y, x + padding_x))
        self.images.add(thumbnail)
        return thumbnail

    def decompress_board(self, rle_compressed_board: str):
        """Decompress a running length encoded board back into a list of bit strings.

        Args:
            rle_compressed_board: Run length encoded board.

        Returns:
            A list of binary strings representing a game board.
        """
        decompressed_board = ''
        current_num = ''
        for char in rle_compressed_board:
            if char.isalpha():
                decompressed_board += char * int(current_num)
                current_num = ''
            else:
                current_num += char
        decompressed_board_l = (
            decompressed_board.replace('E', '1').replace('D', '0').split('N')
        )
        return decompressed_board_l

    def post_popup_menu(self, event: tk.Event, menu: tk.Menu) -> None:
        """Create a popup menu.

        Args:
            event: Event that triggered menu creation.
            menu: Menu to post.
        """
        try:
            menu.post(event.x_root, event.y_root)
            menu.bind('<FocusOut>', lambda *_: menu.unpost())
            menu.focus_set()
        finally:
            menu.grab_release()

    def player_binding(self, event: tk.Event) -> None:
        """Handle right clicks on players."""
        row = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        element = self.tree.identify_element(event.x, event.y)
        if column != '#0' or element != 'text':
            return

        def rename():
            l = LeaderboardRenameDialog(self, self.leaderboard, 'player', row, '')
            self.load_tree()
            self.save_leaderboard()

        def delete():
            a = tk.BooleanVar()
            YesNoDialogue(
                self,
                'Delete Confirmation',
                'Are you sure you want to delete this?',
                a,
            )
            if not a.get():
                return
            self.leaderboard.pop(row)
            self.load_tree()
            self.save_leaderboard()

        menu = tk.Menu(
            event.widget,
            background=self.menu_bg,
            foreground=self.menu_fg,
            activebackground=self.menu_abg,
            activeforeground=self.menu_afg,
        )
        menu.add_command(label='Rename', command=rename)
        menu.add_command(label='Delete', command=delete)
        menu.add_separator()
        menu.add_command(label='Close')
        self.post_popup_menu(event, menu)

    def board_binding(self, event: tk.Event) -> None:
        """Handle right clicks on boards."""
        row = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        element = self.tree.identify_element(event.x, event.y)
        if column != '#0' or element != 'text':
            return

        p = self.tree.parent(row)

        def rename():
            LeaderboardRenameDialog(self, self.leaderboard, 'board', p, row)
            self.load_tree()
            self.tree.item(p, open=True)
            self.save_leaderboard()

        def delete():
            a = tk.BooleanVar()
            YesNoDialogue(
                self,
                'Delete Confirmation',
                'Are you sure you want to delete this?',
                a,
            )
            if not a.get():
                return
            self.leaderboard[p].pop(row.split('@')[-1])
            if not self.leaderboard[p]:
                self.leaderboard.pop(p)
            self.load_tree()
            if p in self.leaderboard:
                self.tree.item(p, open=True)
            self.save_leaderboard()

        menu = tk.Menu(
            event.widget,
            background=self.menu_bg,
            foreground=self.menu_fg,
            activebackground=self.menu_abg,
            activeforeground=self.menu_afg,
        )
        menu.add_command(label='Rename', command=rename)
        menu.add_command(label='Delete', command=delete)
        menu.add_separator()
        menu.add_command(label='Close')
        self.post_popup_menu(event, menu)

    def time_binding(self, event: tk.Event) -> None:
        """Handle right clicks on times."""
        row = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        element = self.tree.identify_element(event.x, event.y)
        if column != '#0' or element != 'text':
            return
        b = self.tree.parent(row)
        p = self.tree.parent(b)
        time = int(self.tree.item(row)['text'].split()[0])
        date = self.tree.item(row)['values'][0]

        def delete():
            bn = b.split('@')[-1]
            a = tk.BooleanVar()
            YesNoDialogue(
                self,
                'Delete Confirmation',
                'Are you sure you want to delete this?',
                a,
            )
            if not a.get():
                return
            entries = self.leaderboard[p][bn]['Entries']
            for i, e in enumerate(entries):
                if e['Time'] == time and e['Date'] == date:
                    break
            entries.pop(i)
            if not entries:
                self.leaderboard[p].pop(bn)
            else:
                self.leaderboard[p][bn]['Entries'] = entries
            self.load_tree()
            if entries:
                self.tree.see(b)
                self.tree.item(b, open=True)
            else:
                self.tree.item(p, open=True)
            self.save_leaderboard()

        menu = tk.Menu(
            event.widget,
            background=self.menu_bg,
            foreground=self.menu_fg,
            activebackground=self.menu_abg,
            activeforeground=self.menu_afg,
        )
        menu.add_command(label='Delete', command=delete)
        menu.add_separator()
        menu.add_command(label='Close')
        self.post_popup_menu(event, menu)

    def save_leaderboard(self) -> None:
        with open(_LEADERBOARD_FILENAME, mode='w') as fp:
            json.dump(self.leaderboard, fp, indent=4)
