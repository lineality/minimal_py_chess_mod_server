"""
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
https://stackoverflow.com/questions/16225872/getting-gunicorn-to-run-on-port-80

sudo apt install authbind
sudo touch /etc/authbind/byport/80
sudo chmod 500 /etc/authbind/byport/80
sudo chown ubuntu /etc/authbind/byport/80

https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html
https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-application-load-balancer.html
https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-application-load-balancer.html

# Note: port use/binding seems to be a main problem issue,
if server mysteriously does not run: try without any port specification:
```
$ gunicorn app:app 
```

requirements.txt:

chess
click
Flask
gunicorn
itsdangerous
Jinja2
MarkupSafe
python-dotenv
Werkzeug
"""

# Import Packages & Libraries
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
#from flask_cors import CORS
import mat_chess
from flask import send_file
import gunicorn
import os

# Required for Flask/Heroku
app = Flask(__name__)

## art for home page
home_page = """<html>
    <body>
      <body style="background-color:black;">
      <font color="00FF00">  
            <div style="line-height:1px">
        <tt> 
<p style="font-size:38px; "> r n b q k b n r </p>
<p style="font-size:38px; "> p p p p p p p p </p>
<p style="font-size:38px; "> . . . . . . . . </p>
<p style="font-size:38px; "> . . . . . . . . </p>
<p style="font-size:38px; "> . . . P . . . . </p>
<p style="font-size:38px; "> . . . . . . . . </p>
<p style="font-size:38px; "> P P P . P P P P </p>
<p style="font-size:38px; "> R N B Q K B N R </p>

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
      </div>
    </body>
</html>
"""


whitelist_dictionary_ip_game = {
"tyrell": """avalon_2601:81:102:1280::92ce,
2601:81:102:1280,pawpaw_data_174:247:80:180, 
28th_76.116.21.34,local_test_127.0.0.1,0.0.0.0""",
"trident":"""avalon_2601:81:102:1280::92ce,
2601:81:102:1280,pawpaw_data_174:247:80:180, 
28th_76.116.21.34,local_test_127.0.0.1,0.0.0.0""",
}

# helper function
def add_ip_to_ip_game_log(add_this, gamename):
    # add to it (append)
    with open(f'games/{gamename}/ip_log.csv', "a") as file_object:
        # read file content
        add_this += ","
        file_object.write( add_this )

# helper function
def get_user_ip():
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

    print(f"user user_ip:\n'{user_ip}'", )

    return user_ip

# helper function
def check_ip_whitelist(gamename, user_ip):
    """
    Also requires another helper function and lookup dict (or other lookup): 
        - get_user_ip()
        - whitelist_dictionary_ip_game = {}
        
    Example Use:
    
    # set inputs:
    gamename = "tyrell"
    the_user_is = get_user_ip()
    
    # run the check:
    boolean_ip_whitelist_check = check_ip_whitelist( gamename, the_user_is)
    
    print(boolean_ip_whitelist_check)
    """
    
    output = False

    try:
        if user_ip in whitelist_dictionary_ip_game[gamename]:
            output = True

    except:
        # default to false, if for whatever reason check does not work
        pass

    return output


# Your Home Screen
@app.route('/')
def home():
    return home_page

###############
# Tyrell Chess
###############
## works by having an HTML interface (render html) but sending 
## the user input to the *_moved endpoint
@app.route('/tyrell')
def tyrell():

    # set inputs:
    gamename = "tyrell"
    the_user_ip = get_user_ip()

    # run the check:
    boolean_ip_whitelist_check = check_ip_whitelist( gamename, the_user_ip)
    print("ip_whitelist match is: ", boolean_ip_whitelist_check)
    
    # setup folders etc
    mat_chess.folder_system_check_setup(gamename)
    
    if boolean_ip_whitelist_check:

        return render_template('tyrell.html')
    
    else:
        print("user not found in whitelist so...try the public sandbox!")
        # return render_template('sandbox.html')
        print("temporary bypass")
        return render_template('tyrell.html')

## gets the input from the html page in templates
@app.route('/tyrell_moved', methods=['POST'])
def tyrell_moved():

    gamename = "tyrell"

    json_obj = {'input_1': request.values['input_1']}
    
    # variables that are use-able by python
    input_1_item = json_obj["input_1"]
    
    #######################
    # Make your game move!
    #######################
    go_to_report = mat_chess.play_mat_chess( gamename, str(input_1_item) )

    # add to IP log
    the_user_ip = get_user_ip()
    add_ip_to_ip_game_log(the_user_ip, gamename)

    #####################
    # save current ascii board string in game folder
    #####################
    board_string = str( mat_chess.raw_board() )

    # save board list string instead of image file
    with open(f'games/{gamename}/current_board_string.txt', "w") as file_object:
        # read file content
        file_object.write( board_string )
        print( f'games/{gamename}/current_board_string.txt updated OK!' )

    # # If redirecting to pic itself
    # """
    # requires: from flask import send_file
    # """
    # filename = 'games/tyrell/current_board.svg'
    ## Version so send to pic
    # return send_file(filename, mimetype='image/svg+xml')
    
    print("from app.py go_to_report is", go_to_report)
    # 
    if go_to_report == 1:
        return render_template(f'{gamename}_report.html')
    
    else:
        return render_template(f'{gamename}.html')


## show current board
@app.route('/tyrell_board')
def tyrell_board():
    filename = 'games/tyrell/current_board.svg'
    return send_file(filename, mimetype='image/svg+xml')

## show current board
@app.route('/tyrell_last_legal_move')
def tyrell_last_legal_move():
    filename = 'games/tyrell/last_legal_move.svg'
    return send_file(filename, mimetype='image/svg+xml')


###############
# Trident Chess
###############
## works by having an HTML interface (render html) but sending 
## the user input to the *_moved endpoint
@app.route('/trident')
def trident():
    # set inputs:
    gamename = "trident"
    the_user_is = get_user_ip()
    
    # run the check:
    boolean_ip_whitelist_check = check_ip_whitelist( gamename, the_user_is)
    
    print("ip_whitelist match is: ", boolean_ip_whitelist_check)
    
    if boolean_ip_whitelist_check:

        return render_template('trident.html')
    
    else:
        print("user not found in whitelist so...try the public sandbox!")
        return render_template('sandbox.html')


## gets the input from the html page in templates
@app.route('/trident_moved', methods=['POST'])
def trident_moved():

    json_obj = {'input_1': request.values['input_1']}
    
    # variables that are use-able by python
    input_1_item = json_obj["input_1"]
    
    #######################
    # Make your game move!
    #######################
    mat_chess.play_mat_chess( "trident", str(input_1_item) )

    # # inspection
    # print( os.listdir() )

    # Move Image to folder for this specific game
    try: 
        os.rename('current_board.svg', 'games/trident/current_board.svg')
        print("picture_moved: OK!")

    except:
        print('no image file...is ok yes?')

    #####################
    # save current ascii board string in game folder
    #####################
    board_string = str( mat_chess.raw_board() )

    # save board list string instead of image file
    with open(f'games/trident/current_board_string.txt', "w") as file_object:
        # read file content
        file_object.write( board_string )
        print( 'games/trident/current_board_string.txt updated OK!' )

    # # If redirecting to pic itself
    # """
    # requires: from flask import send_file
    # """
    # filename = 'games/trident/current_board.svg'
    ## Version so send to pic
    # return send_file(filename, mimetype='image/svg+xml')
    
    ## Version to loop back to play move
    return render_template('trident.html')
    
    
## show current board
@app.route('/trident_board')
def trident_board():

    filename = 'games/trident/current_board.svg'

    return send_file(filename, mimetype='image/svg+xml')


###############
# Sandbox Chess
###############
## works by having an HTML interface (render html) but sending 
## the user input to the *_moved endpoint
@app.route('/sandbox')
def sandbox():
    return render_template('sandbox.html')

## gets the input from the html page in templates
@app.route('/sandbox_moved', methods=['POST'])
def sandbox_moved():

    json_obj = {'input_1': request.values['input_1']}
    
    # variables that are use-able by python
    input_1_item = json_obj["input_1"]
    
    #######################
    # Make your game move!
    #######################
    mat_chess.play_mat_chess( "sandbox", str(input_1_item) )

    # # inspection
    # print( os.listdir() )

    # Move Image to folder for this specific game
    try: 
        os.rename('current_board.svg', 'games/sandbox/current_board.svg')
        print("picture_moved: OK!")

    except:
        print('no image file...is ok yes?')

    #####################
    # save current ascii board string in game folder
    #####################
    board_string = str( mat_chess.raw_board() )

    # save board list string instead of image file
    with open(f'games/sandbox/current_board_string.txt', "w") as file_object:
        # read file content
        file_object.write( board_string )
        print( 'games/sandbox/current_board_string.txt updated OK!' )

    # # If redirecting to pic itself
    # """
    # requires: from flask import send_file
    # """
    # filename = 'games/sandbox/current_board.svg'
    ## Version so send to pic
    # return send_file(filename, mimetype='image/svg+xml')
    
    ## Version to loop back to play move
    return render_template('sandbox.html')
    
    
## show current board
@app.route('/sandbox_board')
def sandbox_board():
    filename = 'games/sandbox/current_board.svg'
    return send_file(filename, mimetype='image/svg+xml')
    

## prints simply: board
@app.route('/white_dragon_ramen')
def white_dragon_ramen():
    # # for whatever recent
    # board_string = str( mat_chess.raw_board() )

    # for tyrell game
    with open(f'games/tyrell/current_board_string.txt', "r") as file_object:
        # read file content
        board_string = file_object.read()

    board_list = board_string.split('\n')

    matrix_chess = f"""<!DOCTYPE html>
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
    return matrix_chess

if __name__ == "__main__":
    # app.run_server(host= '0.0.0.0', port=8050)
    app.run_server
