import tkinter as tk
import tkinter.ttk as ttk
from functools import cached_property
from typing import Literal, TypeAlias, Union

AnyWidget: TypeAlias = tk.Misc

_NOT_CALCULATED = -1

_Directions_Tuple = tuple[
    Literal['nw'],
    Literal['n'],
    Literal['ne'],
    Literal['w'],
    Literal['e'],
    Literal['sw'],
    Literal['s'],
    Literal['se'],
]
_Direction_Literal = Literal['nw', 'n', 'ne', 'w', 'e', 'sw', 's', 'se']
_Neighbours_Dict = dict[_Direction_Literal, Union['BoardSquare', None]]


class BoardSquare(ttk.Label):
    """A toggleable square used in playing Minesweeper.

    Attributes:
        value: Number of mines in the neighbours of the square.
        mine_count: Number of mines in square.
        covered: Square is covered.
        flag_count: Number of flags in the square.
        enabled: Square is enabled.
        neighbour: Neighbouring squares,
            in each of the 8 cardinal and ordinal directions.
    """

    def __init__(
        self, parent: AnyWidget, photoimage: tk.PhotoImage, style: str
    ) -> None:
        """Initializes a BoardSquare based on given parent widget, image, and style.

        Args:
            parent: Parent widget.
            photoimage: Image displayed in the square.
            style: Name of a valid Ttk style.
        """
        super().__init__(master=parent, image=photoimage, style=style)

        self._value: int = _NOT_CALCULATED
        self._mine_count: int = 0
        self._covered: bool = True
        self._flag_count: int = 0
        self._enabled: bool = False
        self._directions: _Directions_Tuple = (
            tk.NW,
            tk.N,
            tk.NE,
            tk.W,
            tk.E,
            tk.SW,
            tk.S,
            tk.SE,
        )
        self._neighbours: _Neighbours_Dict = dict.fromkeys(self._directions)

    image = property(
        fset=lambda self, __new_image: self.config(image=__new_image),
        doc="""Set the image of the square. Write-only.""",
    )

    def __repr__(self) -> str:
        return '<BoardSquare object at ({0}, {1})>'.format(*self.position)

    @property
    def value(self) -> int:
        """Get the value of the square."""
        return self._value

    @property
    def mine_count(self) -> int:
        """Get the number of mines in the square."""
        return self._mine_count

    @property
    def covered(self) -> bool:
        """Get the covered status of the square."""
        return self._covered

    @property
    def flag_count(self) -> int:
        """Get the number of flags in the square."""
        return self._flag_count

    @property
    def enabled(self) -> bool:
        """Get the enabled status of the square."""
        return self._enabled

    @property
    def directions(self) -> _Directions_Tuple:
        """Get a tuple of valid neighbour directions."""
        return self._directions

    @property
    def neighbours(self) -> _Neighbours_Dict:
        """Get the neighbours of the square."""
        return self._neighbours

    @cached_property
    def position(self) -> tuple[int, int]:
        """Get the position of the square in its grid

        Returns:
            A 2-tuple representing the (row, column) position of the square.
        """
        gi = self.grid_info()
        return gi['row'], gi['column']

    def add_mine(self) -> None:
        """Add a mine to the square."""
        self._mine_count += 1

    def calculate_value(self) -> None:
        """Calculate the square's number."""
        self._value = sum(
            sq.mine_count for sq in self._neighbours.values() if sq and sq.enabled
        )

    def add_flag(self) -> None:
        """Add flag to the square."""
        self._flag_count += 1

    def remove_flag(self) -> None:
        """Add flag to the square."""
        self._flag_count -= 1

    def toggle_enable(self) -> None:
        """Toggle the enabled status of the square."""
        self._enabled = not self._enabled

    def uncover(self) -> None:
        """Mark the square as uncovered."""
        self._covered = False

    def reset(self) -> None:
        """Reset the internals of the square."""
        self._value = _NOT_CALCULATED
        self._mine_count = 0
        self._covered = True
        self._flag_count = 0
        self._enabled = False
        self._neighbours = dict.fromkeys(self._directions)
