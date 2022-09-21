"""
curl -v -H "Content-Type: application/json" -X POST -d "{ \"\":\"d2d3\"}" http://127.0.0.1:5000/post_endpoint_1

{'':'d2d3'}

"""


#version 1: Miminal Endpoint API (Flask, Heroku)


## Instructions For Heroku Login & Deploy
#
# $ heroku login
# $ cd my-project/
# $ git init
# $ heroku git:remote -a NAME_OF_YOUR_APP
# $ git add .
# $ git commit -am "make it better"
# $ git push heroku master

## Instructions To create the pipenv in terminal
# pipenv install certifi chardet click flask gunicorn idna itsdangerous jinja2 numpy pandas python-dateutil python-dotenv pytz requests urllib3 werkzeug flask-cors

# ## sample pipenv
# [[source]]
# name = "pypi"
# url = "https://pypi.org/simple"
# verify_ssl = true
#
# [dev-packages]
#
# [packages]
# certifi = "*"
# chardet = "*"
# click = "*"
# flask = "*"
# gunicorn = "*"
# idna = "*"
# itsdangerous = "*"
# jinja2 = "*"
# numpy = "*"
# pandas = "*"
# python-dateutil = "*"
# python-dotenv = "*"
# pytz = "*"
# requests = "*"
# urllib3 = "*"
# werkzeug = "*"
# flask-cors = "*"
#
# [requires]
# python_version = "3.8"

# Import Packages & Libraries
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mat_chess
from flask import send_file

# Optional
dummy_data = {
"A": 1,
"B": "2",
"C": 3.0,
}

# Required for Flask/Heroku
app = Flask(__name__)
CORS(app)

# Notes:
# 1. For herkoku or aws use private environment variables: use dotenv
# 2. Need to install git secrets

# Your Home Screen
@app.route('/tyrell_move')
def home():
    # Displays a basic app written in HTML so that code can be tested directly.
    return render_template('base.html')


@app.route('/tyrell_moved', methods=['POST'])
def tyrell_moved():

    # this gets the json object from the user
    json_obj = {'input_1': request.values['input_1']}
    
    print("request", str(request)) 
    print("request.values", str(request.values))     
    print("json_obj", str(json_obj))    

    # variables that are use-able by python
    input_1_item = json_obj["input_1"]

    mat_chess.play_mat_chess( "tyrell", str(input_1_item) )
    # example of just returning the input

    """
    from flask import send_file
    """
    filename = 'current_board.svg'

    return send_file(filename, mimetype='image/svg+xml')



# input form: {'input_1': "x", 'input_2': "y"}
@app.route('/tyrell', methods=['POST'])
def tyrell():

    # this gets the json object from the user
    json_obj = request.get_json(force=True)
 
    print("json_obj", str(json_obj))

    # These lines brake up the json object into
    # variables that are use-able by python
    input_1_item = json_obj[""]

    mat_chess.play_mat_chess( "tyrell", str(input_1_item) )
    # example of just returning the input

    """
    from flask import send_file
    """
    filename = 'current_board.svg'

    return send_file(filename, mimetype='image/svg+xml')


# dummy data is often useful at the start of a project before you have real data
# no input needed for this endpoint
@app.route('/tyrell')
def data_get_endpoint():

    filename = 'current_board.svg'

    return send_file(filename, mimetype='image/svg+xml')



if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()
