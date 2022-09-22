"""


Minimal flask gunicorn in Production Server
This is extremely minimal for a proof of concept
for running Plotly Dash Community Edition in a Production Server
The overall template for this was take from the plotly dash 
docs page for heroku (see link below), 
then adapted and simplified for general production deployment use.
references:
Less minimal app.py code here:
https://dash.plotly.com/deployment
+ 
correct invocation line here:
https://community.plotly.com/t/error-with-gunicorn-application-object-must-be-callable/31397 

sample end-code:

if __name__ == "__main__":
    app.run_server(host= '0.0.0.0', port=8050)


Test invoke with: 
(but will end when your ec2 terminal session ends, resets, etc.)
    $ gunicorn app:app --bind=0.0.0.0:8050

    
For persistent production you will need: (end with kill process number) 
    (ENV)$ nohup gunicorn app:app --bind=0.0.0.0:8050 &
    or
    (ENV)$ screen gunicorn app:app --bind=0.0.0.0:8050 &

or:
curl -v -H "Content-Type: application/json" -X POST -d "{ \"\":\"d2d3\"}" http://127.0.0.1:5000/post_endpoint_1

{'':'d2d3'}

remember to put :8050 at the end of e.g. default ec2 names

see:
https://flask.palletsprojects.com/en/2.2.x/deploying/gunicorn/ 

https://duckduckgo.com/?t=ffab&q=html+colors&ia=web

https://stackoverflow.com/questions/16225872/getting-gunicorn-to-run-on-port-80
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
#from flask_cors import CORS
import mat_chess
from flask import send_file
import gunicorn

# Optional
dummy_data = {
"A": 1,
"B": "2",
"C": 3.0,
}

# Required for Flask/Heroku
app = Flask(__name__)
#CORS(app)

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
    # app.debug = True
    app.run_server(host= '0.0.0.0', port=8050)