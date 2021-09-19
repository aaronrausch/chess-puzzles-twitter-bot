# Chess Puzzle Twitter Bot
![](README/Chess-Puzzle-Twitter-Bot.png)

This bot posts puzzles that are randomly selected from the open-source Lichess puzzle database.  The caption of each puzzle provides information, along with a direct link.

Images are generated with the help of the chess.cvg library, from parsing FEN.

_Since the file size of ‘lichess_puzzles.csv’ is too large to upload (>300mb), I’ve uploaded ‘reduced_lichess_puzzles.csv’ instead. This file contains the first 10,000 puzzles._

## TO-DO:
* Automate posting, at regular intervals.
* Periodically select puzzles from higher-rated games, or titled players.
* Automatically comment the tweet with the solution, after some period of time.

[Follow the bot on Twitter here.](https://twitter.com/ChessPuzzleBot)