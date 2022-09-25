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
<p style="font-size:20px; "> r n b q k b n r </p>
<p style="font-size:20px; "> p p p p p p p p </p>
<p style="font-size:20px; "> . . . . . . . . </p>
<p style="font-size:20px; "> . . . . . . . . </p>
<p style="font-size:20px; "> . . . P . . . . </p>
<p style="font-size:20px; "> . . . . . . . . </p>
<p style="font-size:20px; "> P P P . P P P P </p>
<p style="font-size:20px; "> R N B Q K B N R </p>
      </div>
    </body>
</html>
"""

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

    return render_template('tyrell.html')

## gets the input from the html page in templates
@app.route('/tyrell_moved', methods=['POST'])
def tyrell_moved():

    json_obj = {'input_1': request.values['input_1']}
    
    # variables that are use-able by python
    input_1_item = json_obj["input_1"]

    mat_chess.play_mat_chess( "tyrell", str(input_1_item) )

    # inspection
    print( os.listdir() )

    # Move Image to folder for this specific game
    try: 
        os.rename('current_board.svg', 'games/tyrell/current_board.svg')
        print("picture_moved: OK!")

    except:
        print('no image file...is ok yes?')

    """
    from flask import send_file
    """
    filename = 'games/tyrell/current_board.svg'

    ## Version so send to pic
    # return send_file(filename, mimetype='image/svg+xml')
    
    ## Version to loop back to play move
    return render_template('tyrell.html')

## show current board
@app.route('/tyrell_board')
def tyrell_board():
    filename = 'games/tyrell/current_board.svg'
    return send_file(filename, mimetype='image/svg+xml')

###############
# Trident Chess
###############
## works by having an HTML interface (render html) but sending 
## the user input to the *_moved endpoint
@app.route('/trident')
def trident():

    return render_template('trident.html')

## gets the input from the html page in templates
@app.route('/trident_moved', methods=['POST'])
def trident_moved():

    json_obj = {'input_1': request.values['input_1']}
    
    # variables that are use-able by python
    input_1_item = json_obj["input_1"]

    mat_chess.play_mat_chess( "trident", str(input_1_item) )

    # inspection
    print( os.listdir() )

    # Move Image to folder for this specific game
    try: 
        os.rename('current_board.svg', 'games/trident/current_board.svg')
        print("picture_moved: OK!")

    except:
        print('no image file...is ok yes?')

    """
    from flask import send_file
    """
    filename = 'games/trident/current_board.svg'

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

    mat_chess.play_mat_chess( "sandbox", str(input_1_item) )

    # inspection
    print( os.listdir() )

    # Move Image to folder for this specific game
    try: 
        os.rename('current_board.svg', 'games/sandbox/current_board.svg')
        print("picture_moved: OK!")

    except:
        print('no image file...is ok yes?')

    """
    from flask import send_file
    """
    filename = 'games/sandbox/current_board.svg'

    ## Version so send to pic
    # return send_file(filename, mimetype='image/svg+xml')
    
    ## Version to loop back to play move
    return render_template('sandbox.html')

## show current board
@app.route('/sandbox_board')
def sandbox_board():
    filename = 'games/sandbox/current_board.svg'
    return send_file(filename, mimetype='image/svg+xml')
    
# ###############
# # Matrix Chess
# ###############
# ## works by having an HTML interface (render html) but sending 
# ## the user input to the *_moved endpoint

# @app.route('/matrix')
# def matrix():

#     # to get saved board file, if not, make a new one
#     try:
#         # save board list string instead of image file
#         with open(f'games/matrix/current_board_string.txt', "r") as file_object:
#             # read file content
#             board_string = file_object.read()
            
#             # inspection
#             print("Got current_board_string.txt, OK!")

#     except:
#         mat_chess.folder_system_check_setup('matrix')
#         # get raw ASCII love
#         board_string = str( mat_chess.raw_board() )

#         # inspection
#         print("reset board_string = ", board_string)
    
#     board_list = board_string.split('\n')

#     matrix_chess_html = f"""
#     <!DOCTYPE html>
#     <html>
#     <body>
#       <body style="background-color:black;"> <tt>
#       <font color="00FF00">  
#         <div style="line-height:1px">
#         <tt> 
#         <p style="font-size:85px; "> {board_list[0]} </p>
#         <p style="font-size:85px; "> {board_list[1]} </p>
#         <p style="font-size:85px; "> {board_list[2]} </p>
#         <p style="font-size:85px; "> {board_list[3]} </p>
#         <p style="font-size:85px; "> {board_list[4]} </p>
#         <p style="font-size:85px; "> {board_list[5]} </p>
#         <p style="font-size:85px; "> {board_list[6]} </p>
#         <p style="font-size:85px; "> {board_list[7]} </p>
#           </div>
#         <form action='/matrix_moved' method="post">
#             <input type="text" name="input_1" style="font-size:40px; placeholder="from to">
#             <input type="submit" style="font-size:40px; value="submit"></form>
#             <br>
#         </form>
#     </body>
#     </html>
#     """

#     with open(f'templates/matrix.html', "w") as file_object:
#         # read file content
#         file_object.write( matrix_chess_html )

#     return render_template('matrix.html')

# ## gets the input from the html page in templates
# @app.route('/matrix_moved', methods=['POST'])
# def matrix_moved():

#     json_obj = {'input_1': request.values['input_1']}

#     # variables that are use-able by python
#     input_1_item = json_obj["input_1"]

#     # make move
#     mat_chess.play_mat_chess( "matrix", str(input_1_item) )

#     board_string = str( mat_chess.raw_board() )

#     # inspection
#     print("(matrix_moved) board_string = ", board_string)

#     board_list = board_string.split('\n')

#     matrix_chess_html = f"""
#     <!DOCTYPE html>
#     <html>
#     <body>
#       <body style="background-color:black;"> <tt>
#       <font color="00FF00">  
#         <div style="line-height:1px">
#         <tt> 
#         <p style="font-size:85px; "> {board_list[0]} </p>
#         <p style="font-size:85px; "> {board_list[1]} </p>
#         <p style="font-size:85px; "> {board_list[2]} </p>
#         <p style="font-size:85px; "> {board_list[3]} </p>
#         <p style="font-size:85px; "> {board_list[4]} </p>
#         <p style="font-size:85px; "> {board_list[5]} </p>
#         <p style="font-size:85px; "> {board_list[6]} </p>
#         <p style="font-size:85px; "> {board_list[7]} </p>
#           </div>
#         <form action='/matrix_moved' method="post">
#             <input type="text" name="input_1" style="font-size:40px; placeholder="from to">
#             <input type="submit" style="font-size:40px; value="submit"></form>
#             <br>
#         </form>
#     </body>
#     </html>
#     """

#     ## 
#     # Write new HTML & new board string.txt
#     ##

#     # write new html
#     with open(f'templates/matrix.html', "w") as file_object:
#         # read file content
#         file_object.write( matrix_chess_html )
#         print( 'templates/matrix.html updated OK!' )

#     # save board list string instead of image file
#     with open(f'games/matrix/current_board_string.txt', "w") as file_object:
#         # read file content
#         file_object.write( board_string )
#         print( 'games/matrix/current_board_string.txt updated OK!' )

#     ## Version to loop back to play move
#     return render_template('matrix.html')

## gets the input from the html page in templates
@app.route('/matrix_board')
def matrix_board():
    # to get saved board file, if not, make a new one
    # try:
    #     # save board list string instead of image file
    #     with open(f'games/matrix/current_board_string.txt', "r") as file_object:
    #         # read file content
    #         board_string = file_object.read()

    #     # inspection
    #     print("OK! Save board string found.")

    # except:
    #     # inspection
    #     print("No Saved board string found. Reset game.")
        
    #     mat_chess.folder_system_check_setup('matrix')
    #     # get raw ASCII love
    #     board_string = str( mat_chess.raw_board() )

    board_string = str( mat_chess.raw_board() )
    # inspection
    print("board_string = ", board_string)

    board_list = board_string.split('\n')

    matrix_chess = f"""<!DOCTYPE html>
    <html>
        <body>
          <body style="background-color:black;">
          <font color="00FF00">  
                <div style="line-height:1px">
            <tt> 
    <p style="font-size:90px; "> {board_list[0]} </p>
    <p style="font-size:90px; "> {board_list[1]} </p>
    <p style="font-size:90px; "> {board_list[2]} </p>
    <p style="font-size:90px; "> {board_list[3]} </p>
    <p style="font-size:90px; "> {board_list[4]} </p>
    <p style="font-size:90px; "> {board_list[5]} </p>
    <p style="font-size:90px; "> {board_list[6]} </p>
    <p style="font-size:90px; "> {board_list[7]} </p>
          </div>
        </body>
    </html>
    """
    return matrix_chess

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    # app.debug = True
    app.run_server(host= '0.0.0.0', port=80)
