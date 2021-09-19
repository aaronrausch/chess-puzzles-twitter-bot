
import chess
import chess.svg
from svglib.svglib import svg2rlg                       # Convert CVG to PDF
from reportlab.graphics import renderPDF
import fitz                                             # Convert PDF to PNG

import tweepy

import os
from csv import reader
from random import choice
from authorization_tokens import *


def twitter_authorization():

    twitter_auth = {
        'CONSUMER_KEY': consumer_key,
        'CONSUMER_KEY_SECRET': consumer_key_secret,
        'ACCESS_KEY': access_key,
        'ACCESS_SECRET': access_key_secret
    }

    auth = tweepy.OAuthHandler(
        twitter_auth['CONSUMER_KEY'], twitter_auth['CONSUMER_KEY_SECRET'])
    auth.set_access_token(
        twitter_auth['ACCESS_KEY'], twitter_auth['ACCESS_SECRET'])

    chess_api = tweepy.API(auth)
    try:
        chess_api.verify_credentials()
        print("Authentication succeeded.")
    except:
        print("Error during authentication.")
        exit()

    return chess_api


def choose_puzzle():

    print('Choosing puzzle...')
    # Imports full list of puzzles
    with open('lichess_puzzles.csv') as puzzles_csv:
        puzzles = reader(puzzles_csv)
        puzzles = list(puzzles)

    puzzle = choice(puzzles)
    return puzzle


def create_puzzle_dictionary(puzzle):
    '''Creates a dictionary with all necessary puzzle values.'''
    return {'PUZZLE_CODE': puzzle[0],
            'PUZZLE_FEN': puzzle[1],
            'FIRST_MOVE': puzzle[2].split()[0],
            'FIRST_PUZZLE_MOVE': 'White' if puzzle[1].split()[-5] == 'b' else 'Black',
            'PUZZLE_RATING': puzzle[3],
            'PUZZLE_URL': puzzle[8]
            }


def play_first_move(puzzle_fen, move):
    '''Plays the first move, and updates the board state.
    This has the effect of setting up the puzzle for the position to solve.
    '''
    board = chess.Board(puzzle_fen)
    move = chess.Move.from_uci(move)
    board.push(move)

    return board


def board_to_svg(board, move):
    ''' Creates SVG of puzzle.
        The color pallette is inspired by Lichess.com.
    '''

    # Checks the last move played
    last_move = chess.Move(chess.parse_square(
        move[0:2]), chess.parse_square(move[2:4]))

    board_svg = chess.svg.board(board, size=900, lastmove=last_move, flipped=not board.turn, coordinates=False,
                                colors={
                                    'square light': '#DFE3E6',
                                    'square dark': '#90A2AC',
                                    'square light lastmove': '#C7D7A0',
                                    'square dark lastmove': '#99B07E'}
                                )
    return board_svg


def svg_to_pdf(board_svg, name):
    '''This function converts the SVG to PDF.
    I would convert the SVG to PNG directly, but due to the complexity of the chess SVG,
    there were frequent glitches. Convering to PDF first, then using a different library
    to convert to PNG, solves this problem.
    '''

    with open(f"{name}.svg", "w") as puzzle_svg:
        # Saves PDF to directory
        puzzle_svg.write(board_svg)
        # Converts SVG to PDF
        chess_pdf = svg2rlg(f'{name}.svg')
        renderPDF.drawToFile(chess_pdf, f'{name}.pdf')
        # Delete SVG
    os.remove(f'{name}.svg')


def pdf_to_image(chess_pdf, name):
    '''This function converts the PDF to a PNG file,
    a format of media accepted by Twitter.
    '''

    chess_doc = fitz.open(chess_pdf)
    # 'Iterating' through the one-page document, and generating a map
    for page in chess_doc:
        # (3, 3) Guarantees high-resolution
        matrix = fitz.Matrix(3, 3)
        puzzle_picture = page.get_pixmap(matrix=matrix)
        puzzle_picture.save(f"{name}.png")
    # Delete PDF, as it is no longer needed
    os.remove(f'{name}.pdf')


def prepare_tweet(chess_api, name, first_puzzle_move, puzzle_rating, puzzle_url):
    '''Prepares and uploads tweet, returns confirmation,
    and cleans up main directory.
    '''

    # Upload puzzle image to Twitter
    chess_puzzle_media = chess_api.media_upload(f'{name}.png')

    # Create text for post
    tweet = f'''
{first_puzzle_move} to move. This puzzle is rated {puzzle_rating} on Lichess.org.
Thank you to Lichess for providing the puzzle database.
Puzzle Details: {puzzle_url}'''

    # Post tweet with image
    chess_api.update_status(status=tweet, media_ids=[
        chess_puzzle_media.media_id])

    # Move image to 'posted_chess_puzzles'
    os.replace(f"{name}.png",
               f"posted_chess_puzzles/{name}.png")

    return print('Puzzle successfully posted.')


def main():

    # Authorizes ChessTwitterBot account
    chess_api = twitter_authorization()

    puzzle = choose_puzzle()

    # Generates a dictionary with all important puzzle information
    puzzle_dictionary = create_puzzle_dictionary(puzzle)
    puzzle_code, puzzle_fen, first_move, first_puzzle_move, puzzle_rating, puzzle_url = puzzle_dictionary.values()

    # Create file name for puzzle
    file_name = f'{puzzle_code}_{puzzle_rating}'

    # Plays the move before puzzle
    board = play_first_move(puzzle_fen, first_move)
    # Generates board SVG, including highlighting the previous move
    board_csv = board_to_svg(board, first_move)

    # Converts SVG -> PDF -> PNG
    svg_to_pdf(board_csv, file_name)
    pdf_to_image(f'{file_name}.pdf', file_name)

    # Tweets
    prepare_tweet(chess_api, file_name, first_puzzle_move,
                  puzzle_rating, puzzle_url)


if __name__ == '__main__':
    main()
