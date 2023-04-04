# FreeForm Minesweeper
FreeForm Minesweeper is the game of Minesweeper as you know and love, but now with the ability to play the classic game on any shape of board you can draw!

## More features on the horizon
  ### What you can expect
  * A Dark theme!
  * A tutorial page!

## Running the game
To play the game, you have two options. You can download the game on your computer using the Linux and Windows releases on the Release pages. This is the recommended option, and the Release pages have their own instructions for downloading and installing Freeform Minesweeper. Alternatively, you can download the source code directly on your machine with the `python freeform_minesweeper.py` command. The source code comes with the requirements of a Python version 3.11.2 or greater. Any source code in active development is not guaranteed to work. For a stable experience, see the Releases. Do *not* run the source code for the installers and uninstallers. They will not function properly. To install the game to your system, see the first option.

## How to start
When you open the game, you're met with a pretty blank window. Before you start playing, you have to give yourself a board to play on! Simply click on a blacked out off square to turn it on, and click on a square that is turned on to turn it back off again. You can also click and drag to paint squares on or off. If drawing a board isn't your fancy, chose one the 4 classic Minesweeper presets at the top: Easy, Medium, Hard, or Expert. These board come with their own difficulty setting so you can truly get the classic experience at the click of a button! You can also use the Fill and Clear buttons to turn all the squares on or off, respectively. After you've drawn yourself a board, select a difficulty from 1 to 4, with 1 being a low amount of mines and 4 being a large amount of mines. If you liked the board you've drawn, you can hit the Save button to play with on it again later, using the Load Button. If you like the board but don't have enough playable squares, or too much, then navigate the toolbar to Edit>Invert to invert all the squares, off to on and on to off. There's also the options in the toolbar too! Click on these to reveal some settings for you to customize. There's more about these settings below. Once you're satisfied, just hit the play button at the top to start the game!

## Game Settings
When you click on the options menu in the toolbar, there are a few settings you can tweak. One of them is the Grace Rule. In Minesweeper, you have the possibility of hitting a mine on your first move. The Grace Rule prevents this from happening and guarantees that you're first move will always be safe. This is on by default, but you can turn it off if you desire. Then there is MultiMine mode. This is a setting, off (Normal mode) by default, that changes the game you're playing in a fun and exciting way. Read below for more information about MultiMine mode. Then there's the Flagless setting. This just makes it so you can't place flags, for those who want to live dangerously. There's also settings for the scale of the board and UI, in case your screen can't handle a massive 64 by 64 Minesweeper experience. To go along with the scaling, there's the Adaptive UI setting, which will show and hide UI elements based on how big the board is. Don't worry about things being hidden; everything found in the UI has a corresponding place in the toolbar. The "More ..." button leads to some additional settings, too. There are the Row and Columns settings. These sliders allow you to customize the size of the game space you are playing if your screen either can't fit the default size or you want to play on a larger board. Additionally, there is the MultiMine mode mine increase. This controls how many more mines appear in MultiMine mode, and is set to a 5% increase initially. If you're looking for more a challenge, you can raise it all the to a 60% increase. And if MultiMine mode is too hard, you can lower it all the way to 0%. This setting has no effect in Normal mode. There's also the MultiMine Probability. This slider changes the probability of getting multimines when playing in multimine mode. It start's at 10% and can go all the way to 90%.

## How to play: Normal mode
Once you've started playing the game, you play it how normal Minesweeper works! Click on a square to reveal it. If it has a number, 1-8, or a blank (0), that's how many of the (up to) 8 potential squares around it have a mine in them. If you click on a mine, you lose! Reveal all the squares without mines to win the game! To help you along your way, there are 2 tools at your disposal: flags and chords. If you're pretty certain you've identified where a mine is, right click on the square to mark it with a flag. These flags can't be revealed like other squares, so you can be safe from any dangerous mines lurking beneath. If you have found and flagged all the mines around a square you can double click on it to chord the square. This reveals all the remaining squares. Pretty handy! But be careful, if you chord with incorrect flags you'll reveal a mine and lose! If you want to play again with the same board, you can click the smiley face new game button. There's also a button to switch between Revealing Mode and Flagging Mode, next to the reset button. In Revealing Mode you play as normal, but in Flagging Mode all your clicks, left and right, will place and remove flags, respectively. You can also toggle this by holding shift. Don't worry, you can still chord in Flagging Mode! If you want to play with a different board, hit the Stop button and you can go back to designing a board.

## How to play: MultiMine mode
In addition to the regular Minesweeper experience, FreeForm Minesweeper also has a MultiMine mode! In MultiMine mode, it's possible for any square on the board to have up to 5 mines inside of it! To follow this, you can flag a square up to 5 times to keep track of all the mines across the board. Because flagging and unflagging is a bit more complicated now, MultiMine mode has some different controls. When in revealing mode, you can only uncover and chord squares with left click and double left click, respectively. Right click does nothing. When in flagging mode, a left click will place a flag on a square and a right click will remove a flag. You can still chord in flagging mode too.

## The Leaderboard
When you beat a game of FreeForm Minesweeper, in either Normal or MultiMine mode, you can save your time to the leaderboard! This allows you to keep track of all your best times as you play, as well as other players tha want to go up against you! You can view the leaderboard at any time using the trophy button. You can also do some management with saved players and times, such as deleting and renaming.


## Features List
 * Default 28 by 30 game space to make boards in
 * 4 Difficulty Levels
	 * 1: ~13% of the squares are mines
	 * 2: ~16% of the squares are mines
	 * 3: ~21% of the squares are mines
	 * 4: ~25% of the squares are mines
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
 * Invert all the squares at once
 * Undo and Redo drawing with Ctrl+z and Ctrl+Shift+Z
 * Switch between Revealing and Flagging modes with the button
 * Switch between Revealing and Flagging modes with Left Shift
 * Flag with right click (Normal Mode)
 * Chording with double click
 * New game button
 * Flag Counter
 * In game timer for time elapsed
 * A handful of fun board shapes to play on (Can be found in File>Sample Boards)
   * The Minesweeper Mine
   * The Minesweeper Flag
   * The Minesweeper Winning face
   * The Leaderboard Trophy
 * MultiMine mode
 * Game settings
   * Enable and disable MultiMine mode
   * Enable and disable the Grace Rule
   * Enable and disable Flagless Mode
   * Change the board scale
   * Change the UI scale
   * Enable and disable the Adaptive UI
   * Change the number of rows in the game space (1 to 60)
   * Change the number of columns in the game space (25 to 60)
   * Change the MultiMine mode mine increase.
   * Change the probability of getting multimines in MultiMine mode


 * Automatically detect if an update is available
 ## Leaderboard Features
 * A leaderboard to keep track of times
   * Times are grouped by boards under a player
   * Times are saved with time in seconds (up to 999) and the date
   * Times keep track if game was played in normal or multimine mode
   * Times and whole boards can be deleted from the leaderboard
   * Boards and players can be renamed in the leaderboard
   * All players and boards must only contain letters (A-Z)
   * All player names must be unique
   * All board names under a player must be unique
 * Thumbnails for all the boards saved.

### Python Requirements (when running source)
 * Python >= 3.11.2