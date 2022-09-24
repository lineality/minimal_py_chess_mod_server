
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

    AWS CloudFormation Please read the official doc : https://docs.aws.amazon.com/acm/latest/userguide/acm-services.html So to install the certificate directly under apache2/nginx configuration you need to obtain the certificate from other third parties like Lets Encrypt, GoDaddy etc. you can read about that here - https://in.godaddy.com/help/manually-install-an-ssl-certificate-on-my-apache-server-centos-5238

On AWS I recommend using an ELB an placing your EC2 instances behind this ELB. This will allow you to select your ACM certificate from ELB itslef. Please read following doc to use classic load balancer with HTTPS https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/ssl-server-cert.html

https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html

https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-application-load-balancer.html

https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-application-load-balancer.html


requirements.txt

chess
click
Flask
gunicorn
itsdangerous
Jinja2
MarkupSafe
python-dotenv
Werkzeug


ubuntu ec2:

sudo apt update
sudo apt upgrade

# reboot

sudo apt install python3.10-venv
git clone https://github.com/lineality/minimal_py_chess_mod_server.git
cd minimal_py_chess_mod_server/
python3 -m venv env
source env/bin/activate
(env) pip install --upgrade pip
(env) pip install -r requirements.txt

sudo apt install authbind
sudo touch /etc/authbind/byport/80
sudo chmod 500 /etc/authbind/byport/80
sudo chown ubuntu /etc/authbind/byport/80

# to test!
(env) gunicorn app:app --bind=0.0.0.0:80

# to Run!! in background
nohup gunicorn app:app --bind=0.0.0.0:8050 &

"""

# Import Packages & Libraries
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
#from flask_cors import CORS
import mat_chess
from flask import send_file
import gunicorn
import os

# Optional
dummy_data = {
"A": 1,
"B": "2",
"C": 3.0,
}

# Required for Flask/Heroku
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
#CORS(app)

# Notes:
# 1. For herkoku or aws use private environment variables: use dotenv
# 2. Need to install git secrets

# Your Home Screen
@app.route('/')
def home():
    # Displays a basic app written in HTML so that code can be tested directly.
    return render_template('base.html')

@app.route('/base_moved', methods=['POST'])
def base_moved():

    # this gets the json object from the user
    json_obj = {'input_1': request.values['input_1']}
    
    print("request", str(request)) 
    print("request.values", str(request.values))     
    print("json_obj", str(json_obj))    

    # variables that are use-able by python
    input_1_item = json_obj["input_1"]

    mat_chess.play_mat_chess( "base", str(input_1_item) )
    # example of just returning the input
    
    # Move Image to folder for that specific game
    try: 
        os.rename('current_board.svg', 'games/base/current_board.svg')

    except:
        print('no image file...is ok yes?')

    """
    from flask import send_file
    """
    filename = 'games/base/current_board.svg'

    #return send_file(filename, mimetype='image/svg+xml')
    return render_template('base.html')

@app.route('/base_board')
def base_board():

    filename = 'games/base/current_board.svg'

    return send_file(filename, mimetype='image/svg+xml')


@app.route('/tyrell')
def tyrell():
    # Displays a basic app written in HTML so that code can be tested directly.
    return render_template('tyrell.html')


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
    
    # Move Image to folder for that specific game
    try: 
        os.rename('current_board.svg', 'games/tyrell/current_board.svg')

    except:
        print('no image file...is ok yes?')

    """
    from flask import send_file
    """
    filename = 'games/tyrell/current_board.svg'

    #return send_file(filename, mimetype='image/svg+xml')
    return render_template('tyrell.html')

@app.route('/tyrell_board')
def tyrell_board():

    filename = 'games/tyrell/current_board.svg'

    return send_file(filename, mimetype='image/svg+xml')



#      |  
#   |  |  |
#   |  |  |
#   ``````'

@app.route('/trident')
def trident():
    # Displays a basic app written in HTML so that code can be tested directly.
    return render_template('trident.html')

@app.route('/trident_moved', methods=['POST'])
def trident_moved():

    # this gets the json object from the user
    json_obj = {'input_1': request.values['input_1']}
    
    print("request", str(request)) 
    print("request.values", str(request.values))     
    print("json_obj", str(json_obj))    

    # variables that are use-able by python
    input_1_item = json_obj["input_1"]

    mat_chess.play_mat_chess( "trident", str(input_1_item) )
    # example of just returning the input
    
    # Move Image to folder for that specific game
    try: 
        os.rename('current_board.svg', 'games/trident/current_board.svg')

    except:
        print('no image file...is ok yes?')

    """
    from flask import send_file
    """
    filename = 'games/trident/current_board.svg'

    #return send_file(filename, mimetype='image/svg+xml')
    return render_template('trident.html')

@app.route('/trident_board')
def trident_board():

    filename = 'games/trident/current_board.svg'

    return send_file(filename, mimetype='image/svg+xml')


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    # app.debug = True
    app.run_server(host= '0.0.0.0', port=8050)
