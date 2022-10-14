"""
test with: gunicorn --bind 0.0.0.0:8050 app:app

Minimal flask gunicorn in Production Server

sample end-code: (note: use port 80 for real deploy, see more below)

if __name__ == "__main__":
    app.run_server(host= '0.0.0.0', port=8050)

Test invoke with: 
(but will end when your ec2 terminal session ends, resets, etc.)
    $ gunicorn app:app --bind=0.0.0.0:8050
    
For persistent production you will need: (end with kill process number) 
    (ENV)$ nohup gunicorn app:app --bind=0.0.0.0:8050 &
    or
    (ENV)$ screen gunicorn app:app --bind=0.0.0.0:8050 &

curl -v -H "Content-Type: application/json" -X POST -d "{ \"\":\"d2d3\"}" http://127.0.0.1:5000/ENDPOINT_NAME

local tesing: remember to put :8050 at the end of e.g. default ec2 names

see:
https://flask.palletsprojects.com/en/2.2.x/deploying/gunicorn/ 
https://duckduckgo.com/?t=ffab&q=html+colors&ia=web
https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-application-load-balancer.html
https://www.askpython.com/python-modules/flask/flask-forms
https://9to5answer.com/debugging-a-flask-app-running-in-gunicorn

127.0.0.1

requirements.txt:

flask
gunicorn
python-dotenv
chess
"""

from other_routes_file import routes_api
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, make_response
import mast_chess
from flask import send_file, redirect
import gunicorn
import os
import chess
import re
from datetime import datetime, timedelta
import json



############################
# Set Your Server URL Here
############################
server_url = "https://y0urm0ve.com"
# server_url = "http://localhost:5000"
# server_url = "http://0.0.0.0:8050"
# server_url = "http://127.0.0.1:5000"


new_routes_string = """#################
#################
# Main Game Page
@app.route("/{gamename}")
def {gamename}():
    gamename = '{gamename}'
    return main_chess_route( gamename )
#################################################
# gets the input from the html page in templates
@app.route('/{gamename}_moved', methods=['POST'])
def {gamename}_moved():
    gamename = '{gamename}'
    return moved_route( gamename )
#####################
# show current board
@app.route('/{gamename}_board')
def {gamename}_board():
    filename = 'games/{gamename}/current_board.svg'
    return send_file(filename, mimetype='image/svg+xml')
#####################
# show current board
@app.route('/{gamename}_last_legal_move')
def {gamename}_last_legal_move():
    filename = 'games/{gamename}/last_legal_move.svg'
    return send_file(filename, mimetype='image/svg+xml')
######################
# Simple Green Board
@app.route('/{gamename}_ramen')
def {gamename}_ramen():
    gamename = '{gamename}'
    return ramen_route( gamename )
# End Chess Routes
###################
"""


###################
# Helper Functions
###################

# helper function
def fake_flask_URL_not_found():
    return """<!doctype html>
    <html lang=en>
    <title>404 Not Found</title>
    <h1>Not Found</h1>
    <p>The requested URL was not found on the server. If you entered the URL manually please    
    check your spelling and try again.</p>"""
    

# helper function
def make_hash(input_string, timestamp_string):
    """
    designed to be a good-enough hash, not relying on libraries
    that includes string and timestamp

    the timestamp kind of functions as a 'secret key'
    as in crypographic 'signing' and verification
    again: not meant to be super world class,
    but light weight and easy to debug,
    not likely to have unexpected or incomprehensible issues
    no external libraries, trust issues, etc. 
    
    the first few digits are less random, so -> removed
    this also keeps the hash from getting huge so quickly

    to make the numbers more significantly different if even one
    input character is changed: add an additional hash if the 
    current hash is odd/even (even picked here)

    for timestamp: use this to get sub-second depth in a string

    from datetime import datetime
    # get time
    timestamp_raw = datetime.utcnow()
    # make readable string
    timestamp = timestamp_raw.strftime('%Y%m%d%H%M%S%f')
    """

    string_to_hash = str(input_string) + str(timestamp_string)

    hash = 1
    for this_character in string_to_hash:
        # 31 or 101 are recommended

        """
        Pick one or the other, not both. 101 tends to be better.
        """
        hash = 101 * (hash + ord(this_character))
        # hash = 31 * (hash + ord(this_character))    

        """
        odd even: reflip
        if the hash is even: hash again
        without this off by one input produces very similar output
        which is contrary to the point of a hash
        """
        if not hash%2:
            # hash = 101 * (hash + ord(this_character))
            hash = 31 * (hash + ord(this_character))

        """
        remove often not-changing first digit(s)
        and also keeps number size from ballooning as quickly
        """
        if len(str(hash)) > 6:
           hash = str(hash)[2:]

        hash = int(hash)

        # # the story so far...
        # print(ord(this_character))
        # print(timestamp)
        # print(hash)

    # print(timestamp)

    hash = str(hash)

    # edge case: if the decimal point shows up
    hash = hash.replace(".","")

    # edge case: if the number is short
    # if len(hash) > 12:
    #     hash = str(hash)[1:]

    return hash


# helper function
def first_folder_system_setup(gamename):
    # setup: make archive folder if none exists 
    if not os.path.exists('games'):
        os.mkdir('games')

    # setup: make archive folder if none exists 
    if not os.path.exists(f'games/{gamename}'):
        os.mkdir(f'games/{gamename}')

    # setup: make archive folder if none exists 
    if not os.path.exists(f'games/{gamename}/archive'):
        os.mkdir(f'games/{gamename}/archive')

    # setup: make log archive
    if not os.path.exists(f'games/{gamename}/ip_log.csv'):
        # make it
        with open(f'games/{gamename}/ip_log.csv', 'w') as file_object:
            # write file content
            file_object.write( "" )

    # setup: make gamelog
    if not os.path.exists(f'games/{gamename}/gamelog.csv'):
        # make it
        with open(f'games/{gamename}/gamelog.csv', 'w') as file_object:
            # write file content
            file_object.write( "" )
    
    print(f"""OK setup: games/{gamename}/ 
        etc. <- done by first_folder_system_setup(gamename)""")





####################
# User IP Functions
####################

# helper function
def get_and_check_user_ip( gamename, remove_ip ):
        # clean combination of sub-functions get + check
        return check_ip_whitelist( gamename, get_user_ip(), remove_ip )

# helper function
def get_user_ip():

    # terminal inspection
    print("""Starting: get_user_ip() """)

    """
    Flask app get ip of user.
    """
    if request.headers.getlist("X-Forwarded-For"):
        user_ip = request.headers.getlist("X-Forwarded-For")[0]
        print("\nuser ip from proxy port forwarding list\n")

    else:
        user_ip = request.remote_addr
        # Terminal Print
        print("\nNormal IP, no proxy or forwarding.\n")

    user_ip = str(user_ip)
    user_ip = user_ip.replace(' ','')

    print(f"user_ip is: '{user_ip}'", )

    return user_ip

# helper function
def check_ip_whitelist( gamename, user_ip, remove_ip ):
    """
    This checks a hash of each ip. 
    for privacy, user IPs are not stored directly

    note: the ip-hash whitelist is a list of strings
    repeat -> type = str
    The type is a string because the number may be very very very long,
    and as an integer it might break the code to be so long.
    (memory issues...ug) 

    get ip hash
    get game-setup timestamp
    check hash of ipv4 + game-setup timestamp

    Also requires another helper function and lookup dict (or other lookup): 
        - get_user_ip()

    whitelist stored with other setup data in:
        f'games/{gamename}/{gamename}_game_setup_dictionary.json'


    Example Use: Setting the result as a variable (optional)

    # set inputs:
    gamename = f"{gamename}"
    the_user_is = get_user_ip()

    # run the check:
    boolean_ip_whitelist_check_result = check_ip_whitelist( gamename, the_user_is)

    print( boolean_ip_whitelist_check_result )
    """

    # terminal inspection
    print("""Starting: check_ip_whitelist(gamename, user_ip)""")

    # default output = False
    output = False

    # Opening JSON file
    with open(f'games/{gamename}/{gamename}_game_setup_dictionary.json', 'r') as file_object:
     
        # Reading from json file
        game_setup_data = json.load( file_object )

    # terminal inspection
    print(""" extracted game_setup_dictionary.json """)
    # print(f""" type: {type(game_setup_data)}, content: {game_setup_data} """)

    try:
        ip_hash_list = game_setup_data['ip_whitelist']
        game_setup_timestamp = game_setup_data['timestamp']
        
        # make a new STRING hash of the current user IP (for later comparison)
        hashed_user_ip =  str( make_hash(user_ip, game_setup_timestamp) )

        # # terminal inspection
        # print(f"""ip type: {type(user_ip)}, ip content: {user_ip} """)
        # print(f"""ip_hash_list type: {type(ip_hash_list)}, ip_hash_list content: {ip_hash_list} """)
        # print("user_ip -> ", user_ip)
        # print("game_setup_timestamp -> ", game_setup_timestamp)        
        # print("new hashed_user_ip -> ", hashed_user_ip)
        # print("hashed_user_ip in ", hashed_user_ip)
        # print(" ip_hash_list",  ip_hash_list)
        # print("hashed_user_ip in ip_hash_list", hashed_user_ip in ip_hash_list)

        ####################################
        # check if ip(hash) is in whitelist
        ####################################
        if hashed_user_ip in ip_hash_list:
        
            # remove that ip from the list
            game_setup_data['ip_whitelist'].remove( hashed_user_ip )
            
            # return value = True
            output = True
            
            if remove_ip == True:
                # re-save
                #################################    
                # Over-Write replace sample.json
                #################################
                # exporting json
                json_object = json.dumps( game_setup_data, indent=0 )
                
                with open(f"games/{gamename}/{gamename}_game_setup_dictionary.json", 'w') as outfile:
                    outfile.write( json_object )            
            
                print("check_ip_whitelist -> Over-Write replace sample.json")
            

        
                # terminal inspection
                print("""  if user_ip in ip_hash_list == True 
                        so: output = True""")

    except Exception as e:
        # default to false, if for whatever reason check does not work
        print(f""" Default to ip-check output = False, something unexpected went wrong: 
               Exception error message = {e} """)

    return output



# helper function
def authenticate_user_true_false__ip_only( gamename ):    
    """
    Returns Boolean: True or False
    
    check cookie
    if cookie exists
    authetnticate cookie
    if cookie authetnated
    return true
    
    if no cookie (yet)
    get IP
    check ip_hash
    if ip_hash check ok
    make cookie
    return true
    
    else
    return false
    """

    # terminal inspection
    print("""Starting: authenticate_user_true_false__ip_only( gamename ) """)


    #######################
    # Part 1: Check Cookie
    #######################
    
    if check_cookie( gamename ):
        return True

    else:
        #############################
        # Part 2: If No Cookie (yet)
        #############################
        print("no cookie found for user for this game")
        print("get_and_check_user_ip(gamename, remove_ip = False)")
        ip_check_result = get_and_check_user_ip(gamename, remove_ip = False)

        if ip_check_result:
            print('ip check ok ->', ip_check_result)
            # if IP in whitelist
            return "ip_only"

        else:
            return False



##########
# Cookies
##########

#def minimal_test_function_set_cookie():
#    resp = make_response("hello ok")
#    resp.set_cookie('label', "value")
#    return resp
 
# Helper Function
def set_the_cookie(gamename, character_name):
    """
    While somewhat cumbersome, 
    in order for the cookie to be set in the browser
    the return object must be sent to the browser
    
    https://pythonbasics.org/flask-cookies/
    but it should be possible to return the user to...
    their site
    """

    # terminal inspection
    print(""" Starting: set_the_cookie(gamename, character_name) """)

    # get time
    timestamp_raw = datetime.utcnow()
    
    # make readable string
    timestamp = timestamp_raw.strftime('%Y%m%d%H%M%S%f')

    # year and a day: game expiration date
    expire_date = datetime.now() + timedelta(days=366)
    
    # 'value' of cookie
    value_string = f"charactername_{character_name},timestamp_{timestamp}"
    
    print("value_string", value_string)
    
    temp_html_page = f"""<!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="refresh" content="0; url={server_url}/{gamename}" />
    <body>
    <body style="background-color:black;">
    </body>
    </head>
    </html>
    """
    
    #############
    # Set Cookie
    #############
    response_object = make_response( temp_html_page, 200)

    response_object.set_cookie(
        f'{gamename}', 
        value=value_string,
        httponly = True,
        expires=expire_date
    )
    print( "made cookie 'response obj' = " )
    # print( "this is set cookie 'response' = ", response_object )


    #####################################################
    # save hash in {gamename}_game_setup_dictionary.json
    #####################################################
    try:
        # Opening JSON file
        with open(f'games/{gamename}/{gamename}_game_setup_dictionary.json', 'r') as file_object:
          
            # Reading from json file
            game_setup_data = json.load(file_object)

        # get timestamp
        timestamp = game_setup_data['timestamp']
            
        # make hash of cookie value
        hashed_value = make_hash( value_string, timestamp )
        
        # print("hashed_value", hashed_value)

        # store cookie value hash in game-setup json
        game_setup_data["hashed_cookies"].append( hashed_value )

        # exporting json
        json_object = json.dumps(game_setup_data, indent=0)
        
        # print('new game json -> ', json_object)
            
        # Writing to sample.json
        with open(f"games/{gamename}/{gamename}_game_setup_dictionary.json", "w") as file_object:
            file_object.write( json_object )

        # terminal inspection
        print(""" extracted game_setup_dictionary.json
                added hashed cookie, saved,
                closed game_setup_dictionary.json again""")

    except Exception as e:
        # terminal print
        print("error saving hash of cookie value in set_the_cookie(gamename), exception = ", e)
        return "Ooopsy doopsy...try contacting the game admin...yeah...maybe that's it..."

    print("Cooking Baking -> OK!")

    return response_object


# helper function
def set_browser_cookie(gamename, character_name):

    # terminal inspection
    print(""" Starting: setcookie(gamename, character_name) """)

    # get time
    timestamp_raw = datetime.utcnow()
    
    # make readable string
    timestamp = timestamp_raw.strftime('%Y.%m.%d.%H.%M.%S.%f')

    # year and a day: game expiration date
    expire_date = datetime.now() + timedelta(days=366)
    
    # 'value' of cookie
    value_string = f"playername_{character_name},timestamp_{timestamp}"
    
    #############
    # Set Cookie
    #############
    response_object = make_response('Setting Cookies, ok!', 200)
    response_object.set_cookie(
        f'{gamename}', 
        value=value_string,
        expires=expire_date
    )
    print( "this is set cookie 'response' = ", response_object )


    #####################################################
    # save hash in {gamename}_game_setup_dictionary.json
    #####################################################
    try:
        # Opening JSON file
        with open(f'games/{gamename}/{gamename}_game_setup_dictionary.json', 'r') as file_object:
          
            # Reading from json file
            game_setup_data = json.load(file_object)

        # get timestamp
        timestamp = game_setup_data['timestamp']
            
        # make hash of cookie value
        hashed_value = make_hash( value_string, timestamp )

        # store cookie value hash in game-setup json
        game_setup_data["hashed_cookies"].append( hashed_value )

        # exporting json
        json_object = json.dumps(game_setup_data, indent=0)
        
        # print('game json -> ', json_object)
            
        # Writing to sample.json
        with open(f"games/{gamename}/{gamename}_game_setup_dictionary.json", "w") as file_object:
            file_object.write( json_object )


        # terminal inspection
        print(""" extracted game_setup_dictionary.json
                added hashed cookie, saved,
                closed game_setup_dictionary.json again""")

        return True


    except Exception as e:
        # terminal print
        print("error saving hash of cookie value in set_the_cookie(gamename), exception = ", e)
        return False


    return response_object


def get_cookie_value( gamename ):
    
    #############
    # Get Cookie
    #############
    game_cookie_string = request.cookies.get( gamename )
    
    # if there is no cookie to be found, this will be None
    if game_cookie_string != None:
        
        return game_cookie_string
    
    else:
        return "no_player"

# Helper Function
def check_cookie(gamename):

    ########################################
    # 1. Get real cookie
    # 2. Get hashed_cookie value from json
    # 3. Get timestamp from json
    # 4. Re-hash real cookie 
    # 5. compare to list in json
    ########################################

    #############
    # Get Cookie
    #############
    game_cookie_string = request.cookies.get( gamename )
    
    # if there is no cookie to be found, this will be None
    if game_cookie_string != None:
        cookie_check_string = f"{gamename}_{game_cookie_string}"
        
        # get /games/gamename/gamename_cookies.txt
        with open(f'games/{gamename}/{gamename}_game_setup_dictionary.json', "r") as file_object:
            # read file content
            game_setup_data = json.load(file_object)

        # print("\ngame_setup_data", game_setup_data)

        # 1. real cookie
        # game_cookie_string

        # 2. get hashed_cookies list
        game_setup_data["hashed_cookies"]
        # print("\ngame_setup_data['hashed_cookies']",game_setup_data["hashed_cookies"])

        # 3 get timestamp
        timestamp = game_setup_data['timestamp']
        # print("\ngame_setup_data['timestamp']",game_setup_data['timestamp'])
        
        # 4 Re-hash real cookie (to compare)
        rehashed_cookie = make_hash( game_cookie_string, timestamp )
        # print("\nrehashed_cookie", rehashed_cookie)

        # 5 compare new hash to json list of authentic hashes
        
        if rehashed_cookie in game_setup_data["hashed_cookies"]:
            print("rehashed_cookie in game_setup_data['hashed_cookies'] -> True!")
            
            # terminal inspection
            print(""" Found Cookie + Cookie OK! -> start game """)
            return True
            
        else:
            # terminal inspection
            print(""" NO matching game cookie found """)

            # terminal inspection
            print(""" setup NO matching game cookie found """)
            return False
    else:
        print(""" NO cookie found at all""")
        return False




def make_game_setup_html( gamename ):

    main_html_page_string = f"""<!DOCTYPE html>
    <html>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <body>
        <tt>
          <body style="background-color:black;">
          <font color="orange">  
          <div style="line-height:1px" >
            <p style="font-size:50px;" >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*</p>
            <p style="font-size:50px;" >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/|</p>
            <p style="font-size:50px;" >&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;|</p>
            <p style="font-size:50px;" >&nbsp;&nbsp;/__|\</p>
            <p style="font-size:50px;" >&nbsp;&nbsp;___|_\__@</p>
            <p style="font-size:50px;" >&nbsp;&nbsp;\______/</p>
            <form action='/{gamename}_moved' method="post">
                <input type="text" name="input_1" style="font-size:50px;" placeholder="d7d5 / report">
                <input type="submit" style="font-size:50px;" value="enter"></form>
                <br>
            </form>
                  </div>
          <img src="https://y0urm0ve.com/{gamename}_board" alt="game board pending" height="850px" width="850px" />
        </object>
        </body>
    </html>
    """
    with open(f'templates/{gamename}.html', 'w') as file_object:
        # write file content
        file_object.write( main_html_page_string )
    print("wrote main_html_page_string")


def make_game_setup_endpoint_routes( gamename ):
    global new_routes_string
    
    mod_string = new_routes_string.replace("{gamename}", gamename)
    
    with open('other_routes_file.py', 'a') as file_object:
        # append (add to) file content
        file_object.write( mod_string )
    print("wrote game_setup_endpoint_routes")
    
    from other_routes_file import routes_api
    
    return True



######################### 
#########################
# route helper functions
#########################
#########################

# route helper function
def public_main_chess_route( gamename ):
    """
    each main gamename hub page
    should authenticate (etc)
    the user, and direct them to:
    1. to more user-setup (if they are not set up yet to play)
    2. to the game (if they are ready to play)
    3. to nothing (if un-authenticate-able)
    """
    
    # terminal inspection
    print(f"""Starting: def {gamename}(): / 
    @app.route("/{gamename}")
    """)


    #########################################
    # Authenticate User Before Starting Game
    #########################################
    
    player_is_authenticated_response = authenticate_user_true_false__ip_only( gamename )

    print(f""" back from <- authenticate_user_true_false__ip_only( {gamename} )
    "player_is_authenticated_response: ", {player_is_authenticated_response}""")
    
    player_is_authenticated_response = True
    
    ###################################################
    # Go to Game | or Setup | or Generic No Page Found
    ###################################################
    
    if player_is_authenticated_response == True:
        return render_template(f"{gamename}.html")

    elif player_is_authenticated_response == "ip_only": 
        return render_template("make_game_access_cookie.html")
        
    else:
        # including "False"
        print(f"""request for @app.route('/{gamename}') 
            was NOT authenticated, so...
            produce a fake URL not found output.
            return fake_flask_URL_not_found()""")
        return fake_flask_URL_not_found()

# route helper function
def main_chess_route( gamename ):
    """
    each main gamename hub page
    should authenticate (etc)
    the user, and direct them to:
    1. to more user-setup (if they are not set up yet to play)
    2. to the game (if they are ready to play)
    3. to nothing (if un-authenticate-able)
    """
    
    # terminal inspection
    print(f"""Starting: def {gamename}(): / 
    @app.route("/{gamename}")
    """)


    #########################################
    # Authenticate User Before Starting Game
    #########################################
    
    player_is_authenticated_response = authenticate_user_true_false__ip_only( gamename )

    print(f""" back from <- authenticate_user_true_false__ip_only( {gamename} )
    "player_is_authenticated_response: ", {player_is_authenticated_response}""")
    
    
    ###################################################
    # Go to Game | or Setup | or Generic No Page Found
    ###################################################
    
    if player_is_authenticated_response == True:
        return render_template(f"{gamename}.html")

    elif player_is_authenticated_response == "ip_only": 
        return render_template("make_game_access_cookie.html")
        
    else:
        # including "False"
        print(f"""request for @app.route('/{gamename}') 
            was NOT authenticated, so...
            produce a fake URL not found output.
            return fake_flask_URL_not_found()""")
        return fake_flask_URL_not_found()

# route helper function
def moved_route( gamename ):
    json_obj = {'input_1': request.values['input_1']}
    
    # variables that are use-able by python
    input_1_item = json_obj["input_1"]
    
    #####################
    # Get character name
    #####################
    character_name =  ( get_cookie_value( gamename ) )
    name_list = character_name.split(',')
    character_name = name_list[0]
    character_name = character_name.replace('charactername_','')
    #print(" character name: ",  character_name)
    
    #######################
    # Make your game move!
    #######################
    player_action = mast_chess.play_mast_chess( gamename, 
                                                character_name, 
                                                str(input_1_item) )


    #################################################
    # save current ascii board string in game folder
    #################################################
    board_string = str( mast_chess.raw_board() )

    # save board list string instead of image file
    with open(f'games/{gamename}/current_board_string.txt', 'w') as file_object:
        # read file content
        file_object.write( board_string )
        print( f'games/{gamename}/current_board_string.txt updated OK!' )


    ################
    # player_action
    ################
    print("from app.py player_action is: ", player_action)
    # 
    if player_action == 'print_report':
        return render_template(f'{gamename}_report.html')


    elif player_action == 'print_action_log':
        try: 
            # append to archive file
            with open(f'games/{gamename}/archive/{gamename}_gamelogs_archive_.csv', 'r') as file_object:
                # write file content
                archive_string = file_object.read()     
            return archive_string
            
        except:
            # if that does not work, go to game
            print("something went wrong:  elif player_action == 'print_archive':")
            return render_template(f'{gamename}.html')


    elif player_action == 'print_character_action_log':
        print("trying to print_character_action_log") 
        try: 
            # append to archive file
            with open(f'games/{gamename}/character_action_log.csv', 'r') as file_object:
                # write file content
                character_action_log_string = file_object.read()     
            return character_action_log_string
            
        except:
            # if that does not work, go to game
            print("something went wrong: elif player_action == 'print_character_action_log':")
            return render_template(f'{gamename}.html')            
        
    else:
        return render_template(f'{gamename}.html')
        
        
# route helper function
def ramen_route( gamename ):
    
    # for trident game
    with open(f'games/{gamename}/current_board_string.txt', "r") as file_object:
        # read file content
        board_string = file_object.read()

    board_list = board_string.split('\n')

    matrix_ramen = f"""<!DOCTYPE html>
    <html>
        <body>
          <body style="background-color:black;">
          <font color="00FF00">  
                <div style="line-height:1px">
            <tt> 
    <p style="font-size:38px; "> {board_list[0]} </p>
    <p style="font-size:38px; "> {board_list[1]} </p>
    <p style="font-size:38px; "> {board_list[2]} </p>
    <p style="font-size:38px; "> {board_list[3]} </p>
    <p style="font-size:38px; "> {board_list[4]} </p>
    <p style="font-size:38px; "> {board_list[5]} </p>
    <p style="font-size:38px; "> {board_list[6]} </p>
    <p style="font-size:38px; "> {board_list[7]} </p>
          </div>
    <p style="font-size:18px; "> 鰻　み　岡　野　エ　た　お　天　ラ　白 </p>
    <p style="font-size:18px; "> 丼　そ　山　菜　ビ　こ　で　丼　ー　竜 </p>
    <p style="font-size:18px; "> 八　カ　の　天　フ　焼　ん　八　メ　 </p>
    <p style="font-size:18px; "> 三　ツ　ラ　ぷ　ラ　き　四　円　ン </p>
    <p style="font-size:18px; "> 百　ラ　ー　ら　イ　三　円 </p>
    <p style="font-size:18px; "> 六　ー　メ　八　十　円 </p>
    <p style="font-size:18px; "> 十　メ　ン　五　円 </p>
    <p style="font-size:18px; "> 三　ン　十　円 </p>
    <p style="font-size:18px; "> 八　万　円 </p>
    <p style="font-size:18px; "> 万　円 </p>
    <p style="font-size:18px; "> 円　</p>
        </body>
    </html>
    """
    return matrix_ramen




#################
################# 
#################
# Main Function
#################
#################
#################
app = Flask(__name__)
app.register_blueprint(routes_api)


#####################
#####################
#####################
# Utility Endpoints
#####################
#####################
#####################

@app.route('/make_game_access_cookie')
def make_game_access_cookie():
    return render_template('make_game_access_cookie.html')

## gets the input from the html page in templates: player_setup
@app.route('/make_game_access_cookie_endpoint', methods=['POST'])
def make_game_access_cookie_endpoint():
    """
    1. get input
    2. check if already authenticated (move long if so)
    3. check IP: if IP on list, set cookie
    5. redirect to game
    6. else...try...flossing?
    """

    # terminal inspection
    print("""Starting: get_player_data_endpoint() / 
    @app.route("/get_player_data_endpoint", methods=['POST']) 
    """)

    json_obj = {'input_1': request.values['input_1'], 'input_2': request.values['input_2']}
    
    # variables that are use-able by python
    input_1_item = json_obj["input_1"]
    input_2_item = json_obj["input_2"] 
 

    ##########################################
    # double check for a cookie for this game 
    # BUT avoid a loop
    ##########################################
    
    gamename = input_1_item.lower()
    
    # if they have a good cookie -> play!
    if check_cookie( gamename ) == True:
        # send to game ->
        return redirect(f"{server_url}/{gamename}")
 
    print("no player cookie yet")
    ######################
    # process character_name
    ######################

    # make both lower-case
    character_name = input_2_item.lower()

    # remove any non alpha-numeric characters
    character_name = ''.join(filter(str.isalnum, character_name))

    # truncate lenth
    if len(character_name) > 12:
        character_name = character_name[:11]

    ##################
    # Double Check IP
    ##################
    ip_check_result = get_and_check_user_ip(gamename, remove_ip = True)
    print("ip checked, result is: ", ip_check_result)

    if ip_check_result == True:
        ##############
        # Make Cookie ...then authenticate the cookie
        ##############
        return set_the_cookie(gamename, character_name)
    
    else:
        return "...Try contacting Dungeon Master..."

@app.route('/url_not_found')
def url_not_found():
    return fake_flask_URL_not_found()


###################
# Setup a new game
###################
@app.route('/setup_game/')
def setup_game():
    # setup_game is same as game_setup, in case reversed by user
    return render_template('game_setup_form.html')
@app.route('/game_setup/')
def game_setup():
    # game_setup is same as setup_game, in case reversed by user
    return render_template('game_setup_form.html')
@app.route('/game_setup_endpoint/', methods = ['POST', 'GET'])
def game_setup_endpoint():
    """
    Set up game file:
    1. create all-important _game_setup_dictionary.json file
    2. make all other folders for game
    """
    if request.method == 'GET':
        return f"""The URL /data is accessed directly. 
            Try going to '/game_setup' """
        
    if request.method == 'POST':
        form_data = request.form
        
        print("form_data", form_data, "type: ", type(form_data))
        print("form_data['gamename']: ", form_data['gamename'])
        
    gamename = form_data['gamename']
    
    # filter gamename characters
    # make both lower-case
    gamename = gamename.lower()

    # remove any non alpha-numeric characters
    gamename = ''.join(filter(str.isalnum, gamename))
    
    # truncate lenth
    if len(gamename) > 12:
        gamename = gamename[:11]


    ######################################
    # check to see if game exists already
    ######################################

    # setup: make archive folder if none exists 
    if os.path.exists(f'games/{gamename}'):
        return "Try again with a different gamename."

    first_folder_system_setup( gamename )

    # get time
    timestamp_raw = datetime.utcnow()
    # make readable string
    timestamp = timestamp_raw.strftime('%Y%m%d%H%M%S%f')

    # game_setup_dict to be written
    game_setup_dict = {
        "gamename": gamename,
        "ip_whitelist": form_data['ip_whitelist'],
        "game_duration_in_days": form_data['game_duration_days'],
        "timestamp": timestamp,
        "hashed_cookies": []
        }

    ##############################################
    # reformat as list of hashed values (in json)
    ##############################################
    input_list = game_setup_dict['ip_whitelist'].split(',')

    for index, value in enumerate(input_list):
        input_list[index] = make_hash( value, game_setup_dict['timestamp'] )

    game_setup_dict['ip_whitelist'] = input_list

    # exporting json
    json_object = json.dumps(game_setup_dict, indent=0)

    #########################    
    # Writing to sample.json
    #########################
    with open(f"games/{gamename}/{gamename}_game_setup_dictionary.json", 'w') as outfile:
        outfile.write( json_object )

    # TODO: 1. make all files; 2. link to game home page

    #########################    
    # Writing .html / routes
    #########################
    # make files
    print("game setup: attempting Writing .html / routes")
    # try:
    make_game_setup_endpoint_routes( gamename )
    make_game_setup_html( gamename )
    #except Exception as e:
    #    print("failed file write game setup -> ", e)

    from other_routes_file import routes_api

    return "now your game exists" 
    # return render_template('{gamename}.html')



#################
#################
#################
# Game Endpoints
#################
#################
#################


#################
#################
# Main Game Page
@app.route("/chess_samplegame")
def chess_samplegame():
    gamename = 'chess_samplegame'
    return public_main_chess_route( gamename )
#################################################
# gets the input from the html page in templates
@app.route('/chess_samplegame_moved', methods=['POST'])
def chess_samplegame_moved():
    gamename = 'chess_samplegame'
    return moved_route( gamename )
#####################
# show current board
@app.route('/chess_samplegame_board')
def chess_samplegame_board():
    filename = 'games/chess_samplegame/current_board.svg'
    return send_file(filename, mimetype='image/svg+xml')
#####################
# show current board
@app.route('/chess_samplegame_last_legal_move')
def chess_samplegame_last_legal_move():
    filename = 'games/chess_samplegame/last_legal_move.svg'
    return send_file(filename, mimetype='image/svg+xml')
######################
# Simple Green Board
@app.route('/chess_samplegame_ramen')
def chess_samplegame_ramen():
    gamename = 'chess_samplegame'
    return ramen_route( gamename )
# End Chess Routes
###################


#################
#################
# Main Game Page
@app.route("/tyrell")
def tyrell():
    gamename = 'tyrell'
    return main_chess_route( gamename )
#################################################
# gets the input from the html page in templates
@app.route('/tyrell_moved', methods=['POST'])
def tyrell_moved():
    gamename = 'tyrell'
    return moved_route( gamename )
#####################
# show current board
@app.route('/tyrell_board')
def tyrell_board():
    filename = 'games/tyrell/current_board.svg'
    return send_file(filename, mimetype='image/svg+xml')
#####################
# show current board
@app.route('/tyrell_last_legal_move')
def tyrell_last_legal_move():
    filename = 'games/tyrell/last_legal_move.svg'
    return send_file(filename, mimetype='image/svg+xml')
######################
# Simple Green Board
@app.route('/tyrell_ramen')
def tyrell_ramen():
    gamename = 'tyrell'
    return ramen_route( gamename )
# End Chess Routes
###################


#################
#################
# Main Game Page
@app.route("/trident")
def trident():
    gamename = 'trident'
    return main_chess_route( gamename )
#################################################
# gets the input from the html page in templates
@app.route('/trident_moved', methods=['POST'])
def trident_moved():
    gamename = 'trident'
    return moved_route( gamename )
#####################
# show current board
@app.route('/trident_board')
def trident_board():
    filename = 'games/trident/current_board.svg'
    return send_file(filename, mimetype='image/svg+xml')
#####################
# show current board
@app.route('/trident_last_legal_move')
def trident_last_legal_move():
    filename = 'games/trident/last_legal_move.svg'
    return send_file(filename, mimetype='image/svg+xml')
######################
# Simple Green Board
@app.route('/trident_ramen')
def trident_ramen():
    gamename = 'trident'
    return ramen_route( gamename )
# End Chess Routes
###################

"""
test with: 
gunicorn --bind 0.0.0.0:8050 app:app
"""
# app.run(host='localhost', port=5000)
if __name__ == "__main__":
    # app.run_server(host= '0.0.0.0', port=8050)
    app.run_server
