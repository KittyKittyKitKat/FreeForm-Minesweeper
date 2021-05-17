# FreeForm Minesweeper
FreeForm Minesweeper is the game of Minesweeper as you know and love, but now with the ability to play the classic game on any shape of board you can draw!

## Running the game
Currently there are no game executables (those will be coming soon!) while the game is in its beta stage. To play FreeForm Minesweeper, just run `python freeform_minesweeper.py` from the command line in the `freeform_minesweeper` directory, with Python version 3.9.0 or greater and Pillow version 8.2.0 or greater.

## How to start
When you open the game, you're met with a pretty blank window. Before you start playing, you have to give yourself a board to play on! Simply click on a blacked out off square to turn it on, and click on a square that is turned on to turn it back off again. You can also click and drag to paint squares on or off. If drawing a board isn't your fancy, chose one the 4 classic Minesweeper presets at the top: Easy, Medium, Hard, or Expert. These board come with their own difficulty setting so you can truly get the classic experience at the click of a button! You can also use the Fill and Clear buttons to turn all the squares on or off, respectively. After you've drawn yourself a board, select a difficulty from 1 to 4, with 1 being a small amount of mines and 4 being a lot of mines. If you liked the board you've drawn, you can hit the Save button to play with it again later, using the Load Button. If you like the board but don't have enough playable squares, or too much, then hit Ctrl-I to invert all the squares, off to on and on to off. Then just hit the play button at the top to start the game!

## How to play
Once you've started playing the game, you play it how normal Minesweeper works! Click on a square to reveal it. If it has a number, 1-8, or a blank (0), that's how many of the 8 potential squares around it have a mine in them. If you click on a mine, you lose! Reveal all the squares without mines to win the game! To help you along your way, there are 2 tools at your disposal: flags and chords. If you're pretty certain you've identified where a mine is, right click on the square to mark it with a flag. These flags can't be revealed like other squares, so you can be safe from any dangerous mines lurking beneath. You can remove a flag by right clicking again, and once you do the square can be revealed again. If you have found and flagged all the mines around a square you can double click on it to chord the square. This reveals all the remaining squares. Pretty handy! But be careful, if you chord with incorrect flags you'll reveal a mine and lose! If you want to play again with the same board, you can click the smiley face new game button. There's also a button to switch between Revealing Mode and Flagging Mode, next to the reset button. In Revealing Mode you play as normal, but in Flagging Mode all your clicks, left and right, will place flags. Don't worry, you can still chord! If you want to play with a different board, hit the Stop button and you can go back to designing a board.

## Features List
 * 30 by 28 game space to make boards in
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
 * Switch between Revealing and Flagging modes
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

## Requirements

### Python Requirements
 * Python, version > 3.9.0

### External Library Requirements
 * Pillow, version > 8.2.0

## Things to be done
 - [ ] Make executables for the game
