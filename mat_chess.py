"""
Modular Amnesiac Turn-based Implementation of Chess
Modular Stateless Turnbased ?

(until rebuilt from scratch)
requires: pip install chess
requires: another file called ~newsvg.py to call on
recommended: venv env

first "first move"
and arrows issue...
replace first move with 'blank board'?

$ python3 -m venv env; source env/bin/activate
$ pip install --upgrade pip
(env) $ pip install chess


invoke with (the way flask server endpoint will)
$ python3
>>> import chess mat_chess

>>> mat_chess.folder_system_check_setup("tyrell")

>>> mat_chess.play_mat_chess("tyrell", "d2d3")


Note: individual move >>> board.push_uci("d2d4")


step:
1 lauch application:
2 load whatever picture is sitting there
3 update game progress
4 get move
5 update pic

 
TODO: 

when is report generated? e.g. if only a report is requested...no moves?

edge case, figure out how to handle restart game blank board print

gamename may be parameter for calling mat_chess.py

log should be specific to game name
as many games will be (ideally) played on same server

maybe reorganize as function-call-able.
try with flask html?

start_new_game command

log and load system

rebuild from simpler parts...

for illegal moves: show an illegal-move image...
maybe current board with red arrow?

report

"""

import chess
import chess.svg
import newsvg
import re
import os
from datetime import datetime
import os
import sys
import shutil


  
# modify svg.py file, so that images are saved as files from terminal
newsvg.makefile()

yes_terms = ["y", "yes", "hai", "ya", "ok", "sure", "one more", "of course"]

arrow_table = {
"a1": chess.A1,
"a2": chess.A2,
"a3": chess.A3,
"a4": chess.A4,
"a5": chess.A5,
"a6": chess.A6,
"a7": chess.A7,
"a8": chess.A8,

"b1": chess.B1,
"b2": chess.B2,
"b3": chess.B3,
"b4": chess.B4,
"b5": chess.B5,
"b6": chess.B6,
"b7": chess.B7,
"b8": chess.B8,

"c1": chess.C1,
"c2": chess.C2,
"c3": chess.C3,
"c4": chess.C4,
"c5": chess.C5,
"c6": chess.C6,
"c7": chess.C7,
"c8": chess.C8,

"d1": chess.D1,
"d2": chess.D2,
"d3": chess.D3,
"d4": chess.D4,
"d5": chess.D5,
"d6": chess.D6,
"d7": chess.D7,
"d8": chess.D8,

"e1": chess.E1,
"e2": chess.E2,
"e3": chess.E3,
"e4": chess.E4,
"e5": chess.E5,
"e6": chess.E6,
"e7": chess.E7,
"e8": chess.E8,

"f1": chess.F1,
"f2": chess.F2,
"f3": chess.F3,
"f4": chess.F4,
"f5": chess.F5,
"f6": chess.F6,
"f7": chess.F7,
"f8": chess.F8,

"g1": chess.G1,
"g2": chess.G2,
"g3": chess.G3,
"g4": chess.G4,
"g5": chess.G5,
"g6": chess.G6,
"g7": chess.G7,
"g8": chess.G8,

"h1": chess.H1,
"h2": chess.H2,
"h3": chess.H3,
"h4": chess.H4,
"h5": chess.H5,
"h6": chess.H6,
"h7": chess.H7,
"h8": chess.H8,
}

###################
# Helper Functions
###################


# helper function
def find_out_whose_turn_it_is(gamelog_movelist):
    
    if not len(gamelog_movelist)%2:
         return "Black"
    else:
        return "White"


# helper function
def raw_board():
    global board
    print(board)
    print("board printed for 'raw_board'")
    return board


# helper function
def check_non_move_commands( move_from_to_input, gamename, is_a_move_flag, print_report_flag, comment ):
    global board
    
    # check for player asking to reprint board:
    if (move_from_to_input == "board"):
        restore_state(gamename, gamelog_movelist)
        
        is_a_move = False
        # print board
        chess.svg.board(board)
        print("printed board on command")
        print(board)
        
        # Move Image to folder for this specific game
        try: 
            os.rename('current_board.svg', f'games/{gamename}/current_board.svg')
            print("picture_moved: OK!")

        except:
            """
            Maybe the insane open source software sometimes does not print?
            """
            print('print_board() no image file...is ok yes?')           
            
        
        
    # check for player asking to see game data report:
    elif (move_from_to_input == "report"):
        # print board
        print( "report" )
        is_a_move = False
        print_report_flag = True

    # check for player asking for a new game
    elif "new" in move_from_to_input:
        # reset game
        reset_state_for_new_game(gamename)
        is_a_move = False
        chess.svg.board(board)
        
        # Move Image to folder for this specific game
        try: 
            os.rename('current_board.svg', f'games/{gamename}/current_board.svg')
            print("picture_moved: OK!")

        except:
            """
            Maybe the insane open source software sometimes does not print?
            """
            print('print_board() no image file...is ok yes?')   
        

    # check for player asking for a new game
    elif "start" in move_from_to_input:
        # reset game
        reset_state_for_new_game(gamename)
        is_a_move = False
        chess.svg.board(board)

    # check for other
    elif ( len(move_from_to_input) != 4 ):
        # reset game
        print( f"\n...some other input...what to do... = ", move_from_to_input)
        is_a_move = False


    ################################
    # 4 parts: check syntax of move
    ################################

    # check move syntax 2
    elif not move_from_to_input[0].isalpha() :
        # reset game
        print( "\nTypo in 1st character of move format.", move_from_to_input)
        is_a_move = False
        comment += "Typo in 1st character of move format."

    # check move syntax 2
    elif not move_from_to_input[1].isdigit() :
        # reset game
        print( "\nTypo in 2nd character of move format.", move_from_to_input)
        is_a_move = False
        comment += "Typo in 2nd character of move format."

    # check move syntax 2
    elif not move_from_to_input[2].isalpha() :
        # reset game
        print( "\nTypo in 3rd character of move format.", move_from_to_input)
        is_a_move = False
        comment += "Typo in 3rd character of move format."
        
    # check move syntax 2
    elif not move_from_to_input[3].isdigit() :
        # reset game
        print( "\nTypo in 4th character of move format.", move_from_to_input)
        is_a_move = False
        comment += "Typo in 4th character of move format."
        

    #########################
    # Passed All Tests: OK!!
    #########################


    else:
        # is a move (if not otherwise indicated, which it wasn't)
        # (is_a_move, print_report_flag)
        is_a_move = True
        print_report_flag = False
    
    return (is_a_move, print_report_flag, comment)


# helper function
def is_move_legal( move_is_ok, first_move, move_from, move_to, was_illegal):
    global board
    print("running legal move check...")
    
    # load input as string
    moves_string = str(board.legal_moves)
    
    # get just text between parentheses
    moves_string = re.findall(r'\(.*?\)', moves_string)[0]
    
    # remove parenthesis
    moves_string = moves_string.strip('()')

    # remove spaces
    moves_string = moves_string.replace(" ", "")

    # remove '#' (checkmate)
    moves_string = moves_string.replace("#", "")

    # remove '+' (check)
    moves_string = moves_string.replace("+", "")

    # remove 's' (stalemate?)
    moves_string = moves_string.replace("s", "")

    legal_moves_list = moves_string.split(',')
    # print("inspect", legal_moves_list)
    
    # leave just the move_to_location
    for index, value in enumerate(legal_moves_list):
        legal_moves_list[index] = value[-2:]
                
    # inspection
    print("\ntest print: legal moves ", legal_moves_list)
    print("\ntest print: board.legal_moves ", board.legal_moves)
    print("\nthis move ", move_from_to_input)

    #############################
    # first check of valid moves
    #############################
    if not ( chess.Move.from_uci( move_from_to_input ) in board.legal_moves ):
        print(f"{move_from_to_input[-2:]}: That would be illegal...")
        print("(game-check)...Let's Go !!")
        move_is_ok = False
        was_illegal = True


        ##############################
        # Second check of valid moves
        ##############################

    elif move_from_to_input[-2:] not in legal_moves_list:
        print(f"{move_from_to_input[-2:]}: That would be illegal...")
        print("(string-check)...Let's Go !!")
        print("legal moves...\n", legal_moves_list)
        move_is_ok = False
        was_illegal = True

    else:
        # print("\nmove is legal")
        
        # mark as no longer first move for the board display arrows
        first_move = False
        
        move_is_ok = True
        was_illegal = False
        
        # set variables
        move_from = move_from_to_input[:2]
        move_to = move_from_to_input[-2:]
        
    # terminal inspection
    print("move_is_ok", move_is_ok)
    print("was_illegal", was_illegal)    
    
    return (move_from, move_to, move_is_ok, was_illegal, first_move)


# helper function
def print_board(first_move,
                was_capture, 
                was_illegal, 
                move_from_to_input, 
                move_from, 
                move_to,
                check_checkmate_flag,
                check_stalemate_flag,
                check_in_check_flag,
                new_game_fresh_board,
                is_a_move_flag):
    global board


    ######################            
    # terminal inspection
    ######################
    if first_move:
        print("first move", first_move)
    
    if was_capture:
        print("check_is_capture_boolean(board)", was_capture)
    
    if was_illegal:
        print("check_is_illegal_boolean(board)", was_illegal)
        
    if not is_a_move_flag:
        print("not a move, no board print")
        
    if check_in_check_flag:
        print("check_in_check_flag = ", check_in_check_flag)

    #########################################
    # Print:  Export case specific svg board
    #########################################
    if not is_a_move_flag:
        return 0
        
    if check_checkmate_flag:
        chess.svg.board(board,
                        fill={ chess.E1: "#00f9ff",
                        chess.E8: "#00f9ff" }
                        )
        # inspection
        print("printed checkmate_board")
        
    elif check_stalemate_flag:

        chess.svg.board(board,
                        fill={ chess.E1: "#00cc00cc",
                        chess.E8: "#00cc00cc" }
                        )
        # inspection
        print("printed checkmate_board")


    elif was_capture:
        
        chess.svg.board(board,
                        fill={arrow_table[move_to]: "#00cc00cc"},
                        arrows=[chess.svg.Arrow(arrow_table[move_from], 
                                                arrow_table[move_to], 
                                                color="#0000cccc")
                                                ]
                                                )
        # inspection
        print("printed piece captured board")   



    elif check_in_check_flag:
        # TODO: this isn't working
        
        chess.svg.board(board,
                        fill={chess.E1: "#00cc00cc", chess.E8: "#00cc00cc" }
                        )
        # inspection
        print("printed in-check board")   


    elif was_illegal:
        illegal_from = move_from_to_input[:2]
        illegal_to = move_from_to_input[-2:]
        
        chess.svg.board(board,
                        fill={arrow_table[illegal_to]: "#cc0000cc"},
                        arrows=[chess.svg.Arrow(arrow_table[illegal_from], 
                                                arrow_table[illegal_to], 
                                                color="#cc0000cc")
                                                ]
                                                )
        # inspection
        print("printed illegal_move_board")

    else:
        #inspection
        # print( "from, to: ", move_from, move_to ) 
        
        chess.svg.board(board, 
                        arrows=[chess.svg.Arrow(arrow_table[move_from], 
                                                arrow_table[move_to], 
                                                color="#0000cccc")
                                                ]
                                                )
                                                
        # inspection
        print("printed default OK-legal-move board")                                                   
                 
    # terminal print
    print("from print_board function", board)
    
    ##########################################
    # current_board pic & last_legal_move pic
    ##########################################
    
    # Move Image to folder for this specific game
    try: 
        os.rename('current_board.svg', f'games/{gamename}/current_board.svg')
        print("picture_moved: OK!")

    except:
        print('print_board() no image file...is ok yes?')    
    
    if not was_illegal:

        try: 
            # Move Image to folder for this specific game
            
            original = f'games/{gamename}/current_board.svg'
            copy = f'games/{gamename}/last_legal_move.svg'

            shutil.copy(original, copy)
            
            print("copied: last legal move pic")

        except:
            print('\nERROR could not update last legal move!!\n')  
    
    return 0


# helper function
def print_special_board(check_stalemate_flag, check_in_check_flag):
    global board
    
    if check_checkmate_flag:
        chess.svg.board(board,
                        fill={ chess.E1: "#00f9ff",
                        chess.E8: "#00f9ff" }
                        )
        # inspection
        print("printed checkmate_board")
        
    elif check_stalemate_flag:

        chess.svg.board(board,
                        fill={ chess.E1: "#00cc00cc",
                        chess.E8: "#00cc00cc" }
                        )
        # inspection
        print("printed checkmate_board")

    elif check_in_check_flag:
        # TODO: this isn't working
        
        chess.svg.board(board,
                        fill={chess.E1: "#cc0000cc", chess.E8: "#cc0000cc" }
                        )
        # inspection
        print("printed in-check board")   



# helper function
# check for capture before making the move
def check_is_capture_boolean(move_from_to_input, first_move):
    global board

    try:
        # only perform check after first move
        if first_move == False:

            # move = board.parse_san( move_to )
            move = board.parse_uci( move_from_to_input )

            if board.is_capture(move):
                return True
                
            else:
                return False
                
        else:  # first move, no check
            return False
    except:
        return False


# helper function
def add_to_game_log(add_this, gamename):
    # add to it (append)
    with open(f'games/{gamename}/gamelog.csv', "a") as file_object:
        # read file content
        add_this += ","
        file_object.write( add_this )


# helper function
def export_game_log():
    """
    TODO
    """
    pass


# helper function gamelog_movelist = import_read_create_game_log_to_list()
def import_read_create_game_log_to_list(gamename):
    global board
    # test print
    print("import_read_create_game_log_to_list")
    print("gamename",gamename)
    
    try:
        # read it
        with open(f'games/{gamename}/gamelog.csv', "r") as file_object:
            # read file content
            data = file_object.read()

        return data.split(',')
        
    except:
        # inspection
        print("no existing log, making new blank log")

        # make it
        with open(f'games/{gamename}/gamelog.csv', "w") as file_object:
            # write file content
            file_object.write( "" )
        
        board = chess.Board()
        
        return []


# helper function
def archive_game_log(gamename):

    # make timestamp for archive name
    date_time = datetime.utcnow()
    timestamp = date_time.strftime('%Y_%m_%d_%H_%M_%S')

    try: 
        # read it (original file)
        with open(f'games/{gamename}/gamelog.csv', "r") as file_object:
            # read file content
            original_log_data = file_object.read()

        # make it (archive file)
        with open(f'games/{gamename}/archive/{timestamp}_gamelog.csv', "w") as file_object:
            # write file content
            file_object.write( original_log_data )
    
    except:
        # terminal print
        print("no gamelog.csv for archive_game_log() to archive.")
    
    return 0


# helper function
def replay_game_log(gamename):
    global board, gamelog_movelist
    
    gamelog_movelist = import_read_create_game_log_to_list(gamename)
    
    # replay each move
    for i in gamelog_movelist:
    
        # print("inspect replay_game_log: ", i)
        
        if len(i) > 3:
            try:
                board.push_uci( i )    
            except Exception as e:
                print(e)
                

# helper function
def restore_state(gamename, gamelog_movelist):
    global board
    # required step: build chess board to start game (class instantiation)
    board = chess.Board()
    
    replay_game_log(gamename)


# helper function
def make_blank_gamelog(gamename):
    # make it
    with open(f'games/{gamename}/gamelog.csv', "w") as file_object:
        # write file content
        file_object.write( "" )


# helper function
def reset_state_for_new_game(gamename):
    global board
    archive_game_log(gamename)
    make_blank_gamelog(gamename)
    board = chess.Board()


# helper function
def folder_system_check_setup(gamename):
    global board
    # setup: make archive folder if none exists 
    if not os.path.exists('games'):
        os.mkdir('games')

    # setup: make archive folder if none exists 
    if not os.path.exists(f'games/{gamename}'):
        os.mkdir(f'games/{gamename}')

    # setup: make archive folder if none exists 
    if not os.path.exists(f'games/{gamename}/archive'):
        os.mkdir(f'games/{gamename}/archive')

    # setup: make archive folder if none exists 
    if not os.path.exists(f'games/{gamename}/current_board.svg'):
        board = chess.Board()
        chess.svg.board(board)
        # Move Image to folder for this specific game
        try: 
            os.rename('current_board.svg', f'games/{gamename}/current_board.svg')
            print("during folder_system_check_setup: new picture_moved: OK!")

        except:
            print('new setup failed to make board')

    # setup: make log archive
    if not os.path.exists(f'games/{gamename}/ip_log.csv'):
        # make it
        with open(f'games/{gamename}/ip_log.csv', "w") as file_object:
            # write file content
            file_object.write( "" )

    # setup: make gamelog
    if not os.path.exists(f'games/{gamename}/gamelog.csv'):
        # make it
        with open(f'games/{gamename}/gamelog.csv', "w") as file_object:
            # write file content
            file_object.write( "" )

# helper function
def make_html_report(whose_move_is_it,
                    game_over_flag,
                    check_in_check_flag,
                    check_checkmate_flag,
                    check_stalemate_flag,
                    comment,
                    gamelog_movelist):

    print("make_report, checking legal moves: ", board.legal_moves)

    # load input as string
    moves_string = str(board.legal_moves)
    
    # get just text between parentheses
    moves_string = re.findall(r'\(.*?\)', moves_string)[0]

    html_report = f"""<!DOCTYPE html>
    <html>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <body>
        <tt>
          <body style="background-color:black;">
          <font color="orange">  
          <div style="line-height:1px">
            <p style="font-size:75px; ">  Tyrell : Report </p>
            <p style="font-size:30px; ">  Enter move cordinates: space-from & space-to. </p>
            <p style="font-size:30px; ">  </p>
            <p style="font-size:30px; ">  E.g. From space d7 to space d5 is entered as: </p>
            <p style="font-size:60px; ">  d7d5 </p>
            <p style="font-size:35px; "> Non-Move input Options: </p>
            <p style="font-size:20px; "> "new" -> For new game: start from scratch </p>
            <p style="font-size:20px; "> "board" -> To refresh the board image </p>
            <p style="font-size:20px; "> "report" -> For game data </p> 
          </div>
          
            <form action='/tyrell_moved' method="post">
            <input type="text" name="input_1" style="font-size:50px;" placeholder="type your move here">
            <input type="submit" style="font-size:50px;" value="enter"></form>
                <br>
            </form>
            <p style="font-size:60px; ">  Current Board </p>
            <img src="https://y0urm0ve.com/tyrell_board" alt="game board pending" height="850px" width="850px" />
          

            <p style="font-size:30px; "> </p>        
            <p style="font-size:30px; "> Whose turn is it? : {whose_move_is_it}
            <br> Game Over : {game_over_flag} 
            <br> In Check : {check_in_check_flag} 
            <br> Checkmate : {check_checkmate_flag} 
            <br> A Stalemate : {check_stalemate_flag} 
            </p>
            
            <p style="font-size:30px; "> The History : {gamelog_movelist[:-1]} </p>
            <p style="font-size:10px; "> Legal Moves List : {moves_string} </p>
            <p style="font-size:30px; "> </p>
                  

          
        <p style="font-size:60px; "> Last Legal Move Board </p>
        <img src="https://y0urm0ve.com/tyrell_last_legal_move" alt="game board pending" height="850px" width="850px" />
            
            
        <p style="font-size:20px; "> Play <a href="https://y0urm0ve.com/tyrell">y0urm0ve.com/tyrell</a> </p>
        <p style="font-size:20px; "> Report <a href="https://y0urm0ve.com/tyrell_report">y0urm0ve.com/tyrell_report</a> </p>
        <p style="font-size:20px; "> Board <a href="https://y0urm0ve.com/tyrell_board">y0urm0ve.com/tyrell_board</a> </p>
        <p style="font-size:20px; "> Legal Moves <a href="https://y0urm0ve.com/tyrell_last_legal_move">y0urm0ve.com/tyrell_last_legal_move</a> </p>
        <p style="font-size:20px; "> Ramen <a href="https://y0urm0ve.com/white_dragon_ramen">y0urm0ve.com/white_dragon_ramen</a> </p>
            
        </body>
    </html>
        """
    return html_report

# variables
gamelog_movelist = [] 
move_from = ""
move_to = ""
gamename = ""
move_from_to_input = ""

board = chess.Board()

############
############
# Main Game
############
############
def play_mat_chess(user_gamename_input, user_move_from_to_input):
    global board
    global move_from, move_to, gamename, move_from_to_input
    global gamelog_movelist
    
    comment = ""
    whose_move_is_it = "White"
    
    gamename = user_gamename_input.lower()
    move_from_to_input = user_move_from_to_input.lower()
    
    
    ############################
    # Process & Check Raw input
    ############################

    # remove any non alpha-numeric characters
    move_from_to_input = ''.join(filter(str.isalnum, move_from_to_input))

    # Set Flags
    game_over_flag = False
    check_checkmate_flag = False
    check_stalemate_flag = False
    check_in_check_flag = False
    move_still_under_review = True
    first_move = True
    new_game_fresh_board = True
    was_capture = False
    was_illegal = False
    move_is_ok = True
    move_still_under_review = True
    is_a_move_flag = True
    whose_turn_white_true_flag = True
    print_report_flag = False
    
    ##################
    # Start Game Turn
    ##################
    # check that folder system exists, create if not there already
    folder_system_check_setup(gamename)


    #######################################
    # Move: Next Turned-Based Modular Turn
    #######################################

    ########################################
    # Get Game History & Current Game State
    ########################################
    restore_state(gamename, gamelog_movelist)


    ####################################################
    # check for player options other than making a move
    ####################################################
    is_a_move_flag, print_report_flag, comment = check_non_move_commands( move_from_to_input, 
                                                gamename, 
                                                is_a_move_flag,
                                                print_report_flag,
                                                comment)
    
    # exit game early
    if (not is_a_move_flag) & (not print_report_flag):
        print("action not a game move: ", move_from_to_input)
        return 0

    # TODO is this the right place????
    # if print_report_flag:
    #     print("check for options: 'report' selected: ", print_report_flag, move_from_to_input)
    #     return 1
    
    
    
    
    # check only if a move:
    if is_a_move_flag:
        #################
        # Move is Legal?
        #################

        move_from, move_to, move_is_ok, was_illegal, first_move = is_move_legal( move_is_ok, 
                                                                                     first_move, 
                                                                                     move_from, 
                                                                                     move_to, 
                                                                                     was_illegal )

        ###################
        # Will be Capture?
        ###################
        was_capture = check_is_capture_boolean( move_from_to_input, 
                                                first_move)
    
    # Do only if a move:
    if is_a_move_flag:        
        ##################
        ##################
        # Make Legal Move
        ##################
        ##################
        
        # terminal inspection
        print("move_is_ok", move_is_ok)
        print("was_illegal", was_illegal)
        
        try:
            # if move is valid, check for end of game
            if (move_is_ok == True) & (was_illegal == False):
                # make move
                board.push_uci( move_from_to_input )  
                
                # update log
                add_to_game_log( move_from_to_input, gamename )
        except Exception as e:
            print(e)


    ################
    # Is in Check ?
    ################
    print("inspection: checking mates...\n")
    if board.is_check():
        check_in_check_flag = True
        print("Let's The Check !")
    else:
        check_in_check_flag = False
        print("Not in check.")
        
        
    ######################
    # Check if Game Over
    ######################

    # print("inspection: checking mates...\n")
    if board.is_checkmate():
        game_over_flag = True
        check_checkmate_flag = True
        move_still_under_review = False
        print("Let's checkmate !!")

    if board.is_stalemate():
        game_over_flag = True
        move_still_under_review = False
        print("Let's stalemate !!")


    ## TODO check length of log for number of moves, if bother
    #if len(gamelog_movelist) > 74:
    #    print("75 moves, game is a draw...YAY!")
    #    return 0

    ##############
    # print board
    ##############

    print_board(first_move,
                was_capture, 
                was_illegal, 
                move_from_to_input, 
                move_from, 
                move_to,
                check_checkmate_flag,
                check_stalemate_flag,
                check_in_check_flag,
                new_game_fresh_board,
                is_a_move_flag)
        
    # except Exception as e:  # 3rd backup catchall check for valid moves
    #     print("move error: e = ", e)
    #     move_is_ok = False
    #     was_illegal = True

        
    ######################
    # Game over etc check
    ######################
    """
    TODO: 
    probably find some way to visually differentiate these one board print

    just for terminal inspection for now to see if system is working
    """
    print("\n\nGame over etc check section: flag check for board print\n")
    if check_checkmate_flag:
        # terminal inspection
        print("CheckmAte!")
    else:
        print("no checkmate")

    if check_stalemate_flag:
        # terminal inspection
        print("...oooo StalemaTe...")
    else:
        print("no stalemate")
        
    if game_over_flag:
        # terminal inspection
        print("\nGames' ovEr\n")
        print("\nGames' ovEr\n")
        print("\nGames' ovEr\n")
        print("\nGames' ovEr\n")
    else:
        print("not 'game over'\n")

    ######################################################
    # If check, checkmate, stalemate: print special board
    ######################################################

    


    ########################
    # Whose turn is it now?
    ########################
    """
    Bare with me:
    The current answer to "Whose turn is it now?"
    can be found out by looking at the number of past legal moves.
    The game starts on white, so even number of past moves mean
    that it is white's turn.
    HOWEVER, the move list has a blank latest entry, so 
    as usual in computer science
    the answer is off by one and backwards:
    
    The method "not YOUR_NUMBER%2" is a short clean way to ask:
    "Is this number even?"
    Which here looks like this: "if not len(gamelog_movelist)%2"
    
    So: 
    Is Even? == True ==> It is black's turn.
    Is Even? == False ==> Is it White's turn.
    """
    # Refresh game move list
    gamelog_movelist = import_read_create_game_log_to_list(gamename)
    
    # Find out whose turn it is...!
    whose_move_is_it = find_out_whose_turn_it_is(gamelog_movelist)


    #####################
    # Update Report Page
    #####################
    
    print("Updating report...")

    # comment:
    if was_capture:
        comment += "was capture"
    
    with open(f'templates/{gamename}_report.html', "w") as file_object:
        # write file content
        html_text = make_html_report(whose_move_is_it,
                                    game_over_flag,
                                    check_in_check_flag,
                                    check_checkmate_flag,
                                    check_stalemate_flag,
                                    comment,
                                    gamelog_movelist)
        
        file_object.write( html_text )

    print("Report updated..\n")


    ####################
    # Finish / Wrap Up
    ####################
    # if not game_over_flag:
        ## terminal inspection
        # print("Game is Not Over")
        
    print("\nProcessing of Modular Action Taken is Completed: OK!\n")
    
    print("Game history is...")
    
    # refresh list
    gamelog_movelist = import_read_create_game_log_to_list(gamename)
    print(str(gamelog_movelist))
    
    print("final return check: print_report_flag", print_report_flag)
    
    if print_report_flag is True:
        return 1
    
    else:
        return 0


