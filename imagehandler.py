from pathlib import Path
from tkinter import PhotoImage
from typing import Final, Literal, TypeAlias


class ImageHandler:
    """Handler for loading and lookup of various game images.

    This handler also serves the purpose of keeping a strong reference
    to all of the PhotoImages used, so that they are not garbage collected
    when used inside of a Tkinter widget.
    """

    SM_SQUARE: Final = '16x16'
    LG_SQUARE: Final = '32x32'
    SM_SEVSEG: Final = '13x23'
    LG_SEVSEG: Final = '26x46'
    LIGHT: Final = 'light'
    DARK: Final = 'dark'
    BOARD: Final = 'board'
    UI: Final = 'ui'
    SEVSEG: Final = 'sevseg'
    _ImageSize: TypeAlias = Literal['16x16', '32x32', '13x23', '26x46']
    _ImageCategory: TypeAlias = Literal['board', 'ui', 'sevseg']
    _ImageTheme: TypeAlias = Literal['light', 'dark']

    def __init__(self) -> None:
        """Initialize an ImageHandler.

        Ideally ImageHandler should only be instantiated once.
        Can only be instantiated after the Tkinter root window is created.
        """
        self.__image_cache: dict[Path, PhotoImage] = {}

    def lookup(
        self,
        size: _ImageSize,
        theme: _ImageTheme,
        category: _ImageCategory,
        name: str,
    ) -> PhotoImage:
        """Fetch an image based on its size, category, and name.

        Args:
            size: Size of image, one of "16x16", "32x32", "13x26", "26x46".
            theme: Theme of the image, one of "light" or "dark".
            category: Category of the image, one of "board", "sevseg", or "ui".
            name: Name of the image.

        Raises:
            ValueError: The image could not be fetched with given parameters.

        Returns:
            The PhotoImage instance of the image fetched.
        """
        image_path = Path('assets') / category / theme / size / f'{name}.png'
        if not image_path.exists():
            raise ValueError(f'No such image exists: {image_path}')
        if image_path in self.__image_cache:
            return self.__image_cache[image_path]
        photoimage = PhotoImage(file=str(image_path.resolve()))
        self.__image_cache[image_path] = photoimage
        return photoimage
