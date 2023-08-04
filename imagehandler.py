# Copyright © Simon Harris-Palmer 2023. All rights reserved.

from enum import Enum
from pathlib import Path
from tkinter import PhotoImage


class ImageHandler:
    """Handler for loading and lookup of various game images.

    This handler also serves the purpose of keeping a strong reference
    to all of the PhotoImages used, so that they are not garbage collected
    when used inside of a Tkinter widget.
    """

    class ImageSize(Enum):
        SM_SQUARE = '16x16'
        LG_SQUARE = '32x32'
        SM_SEVSEG = '13x23'
        LG_SEVSEG = '26x46'

    class ImageTheme(Enum):
        LIGHT = 'light'
        DARK = 'dark'

    class ImageCategory(Enum):
        BOARD = 'board'
        UI = 'ui'
        SEVSEG = 'sevseg'

    def __init__(self) -> None:
        """Initialize an ImageHandler.

        Ideally ImageHandler should only be instantiated once.
        Can only be instantiated after the Tkinter root window is created.
        """
        self.__image_cache: dict[Path, PhotoImage] = {}

    def lookup(
        self,
        size: ImageSize,
        theme: ImageTheme,
        category: ImageCategory,
        name: str,
    ) -> PhotoImage:
        """Fetch an image based on its size, category, and name.

        Args:
            size: Size of image.
            theme: Theme of the image.
            category: Category of the image.
            name: Name of the image.

        Raises:
            ValueError: The image could not be fetched with given parameters.

        Returns:
            The PhotoImage instance of the image fetched.
        """
        image_path = (
            Path('assets') / category.value / theme.value / size.value / f'{name}.png'
        )
        if not image_path.exists():
            raise ValueError(f'No such image exists: {image_path}')
        if image_path in self.__image_cache:
            return self.__image_cache[image_path]
        photoimage = PhotoImage(file=str(image_path.resolve()))
        self.__image_cache[image_path] = photoimage
        return photoimage
