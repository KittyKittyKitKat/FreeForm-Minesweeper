# FreeForm Minesweeper
FreeForm Minesweeper is the game of Minesweeper as you know and love, but now with the ability to play the classic game on any shape of board you can draw!

## Version 2.0 is coming soon!
  ### What you can expect
  * A score keeping system to keep track of all your best times!
  * Support for theming, with an included dark theme!
  * Undoing and redoing when drawing boards!
  * A better (un)installation system!
  * Lots of bugfixes!

## Running the game
To play the game, you have two options. You can download the game on your computer using the Linux and Windows releases on the Release pages. This is the recommended option, and the Release pages have their own instructions for downloading and installing Freeform Minesweeper. Alternatively, you can download the source code directly on your machine with the `python freeform_minesweeper.py` command. The source code comes with the requirements of a Python version 3.9.0 or greater and Pillow version 8.3.2 or greater. Do *not* run the source code for the installers and uninstallers. They will not function properly. To install the game, see the first option.

## How to start
When you open the game, you're met with a pretty blank window. Before you start playing, you have to give yourself a board to play on! Simply click on a blacked out off square to turn it on, and click on a square that is turned on to turn it back off again. You can also click and drag to paint squares on or off. If drawing a board isn't your fancy, chose one the 4 classic Minesweeper presets at the top: Easy, Medium, Hard, or Expert. These board come with their won difficulty setting so you can truly get the classic experience at the click of a button! You can also use the Fill and Clear buttons to turn all the squares on or off, respectively. After you've drawn yourself a board, select a difficulty from 1 to 4, with 1 being a small amount of mines and 4 being a lot of mines. If you liked the board you've drawn, you can hit the Save button to play with it again later, using the Load Button. If you like the board but don't have enough playable squares, or too much, then hit Ctrl-I to invert all the squares, off to on and on to off. There's also the options button at the top. Click on this to reveal a couple settings for can customize. There's more about these settings below. Once you're satisfied, just hit the play button at the top to start the game!

## Game Settings
When you click on the options button, there are a few settings you can tweak. First is the Grace Rule. In Minesweeper, you have the possibility of hitting a mine on your first move. The Grace Rule prevents this from happening and guarantees that you're first move will always be safe. This is on by default, but you can turn it off if you desire. Then there is MultiMine mode. This is a setting, off (Normal mode) by default, that changes the game you're playing in a fun and exciting way. Read below for more information about MultiMine mode. Additonally, there is the MultiMine mode mine increase. This controls how many more mines appear in MultiMine mode, and is set to a 5% increase initially. If you're looking for more a challenge, you can raise it all the to a 60% increase. And if MultiMine mode is too hard, you can lower it all the way to 0%. This setting has no effect in Normal mode. There's also the MultiMine Probability. This slider changes the probability of getting multimines when playing in multimine mode. It start's at 10& and can go all the way to 90%. Then there's the Flagless setting. This just makes it so you can't place flags, for those who want to live dangerously. Finally are the Row and Columns settings. These sliders allow you to customize the size of the game space you are playing if your screen either can't fit the default size or you want to play on a larger board.

## How to play: Normal mode
Once you've started playing the game, you play it how normal Minesweeper works! Click on a square to reveal it. If it has a number, 1-8, or a blank (0), that's how many of the 8 potential squares around it have a mine in them. If you click on a mine, you lose! Reveal all the squares without mines to win the game! To help you along your way, there are 2 tools at your disposal: flags and chords. If you're pretty certain you've identified where a mine is, right click on the square to mark it with a flag. These flags can't be revealed like other squares, so you can be safe from any dangerous mines lurking beneath. If you have found and flagged all the mines around a square you can double click on it to chord the square. This reveals all the remaining squares. Pretty handy! But be careful, if you chord with incorrect flags you'll reveal a mine and lose! If you want to play again with the same board, you can click the smiley face new game button. There's also a button to switch between Revealing Mode and Flagging Mode, next to the reset button. In Revealing Mode you play as normal, but in Flagging Mode all your clicks, left and right, will place flags. You can also toggle this by pressing Ctrl-F. Don't worry, you can still chord! If you want to play with a different board, hit the Stop button and you can go back to designing a board.

## How to play: MultiMine mode
In addition to the regular Minesweeper experience, FreeForm Minesweeper also has a MultiMine mode! In MultiMine mode, it's possible for any square on the board to have up to 5 mines inside of it! To follow this, you can flag a square up to 5 times to keep track of all the mines across the board. Because flagging and unflagging is a bit more complicated now, MultiMine mode has some different controls. When in revealing mode, you can only uncover and chord squares with left click and double left click, respectively. When in flagging mode, a left click will place a flag on a square and a right click will remove a flag. You can still chord in flagging mode too.


## Features List
 * Default 30 by 28 game space to make boards in
 * 4 Difficulty Levels
	 * 1: 13% of the squares are mines
	 * 2: 16% of the squares are mines
	 * 3: 20.7% of the squares are mines
	 * 4: 25% of the squares are mines
 * 4 Board Presets
	 * Easy: 9 by 9 board, with a difficulty of 1
	 * Medium: 16 by 16 board, with a difficulty of 2
	 * Hard: 30 by 16 board, with a difficulty of 3
	 * Expert: 30 by 28 board, with a difficulty of 4
 * Save the current board as a file
 * Load in saved board files
 * Fill the game space with squares
 * Empty the game space
 * Click and drag to draw when designing a board
 * Invert all the squares at once with Ctrl-I
 * Switch between Revealing and Flagging modes button
 * Switch between Revealing and Flagging modes with Ctrl-F
 * Flag with right click
 * Chording with double click
 * New game smiley button
 * Flag Counter
 * In game timer
 * A handful of fun board shapes to play on
   * The Minesweeper mine (mine.ffmnswpr)
   * The Minesweeper flag (flag.ffmnswpr)
   * The Minesweeper winning face (winface.ffmnswpr)
 * An optional font to play the game with. Highly recommended to install! Credit to [Gezoda on FontStruct](https://fontstruct.com/fontstructors/593973/gezoda)
 * MultiMine mode
 * Game settings
   * Grace Rule toggle
   * Enable MultiMine mode
   * Change the MultiMine mode mine increase.
   * Change the probability of getting multimines in MultiMine mode
   * Play the game with no flags
   * Change the number of rows in the game space (1 to 60)
   * Change the number of columns in the game space (25 to 60)
 * Automatically detect if an update is available

## Requirements (When running source)

### Python Requirements
 * Python, version >= 3.9.0

### Library Requirements
 * TKinter, verison >= 8.6
 * Pillow, version >= 8.3.2
 * requests, verison >= 2.25.1
