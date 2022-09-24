# m.a.t. pychess

mod of pip install chess

m Modular
a Amnesiac
t Turnbased

m.a.t. gaming system

endpoint oriented


///////////////////////////////////////////////////////////////

debugging:
make env
$ python3
$ import chess, mat_chess
$ 






//////////////////////////////////////////////////////////


python3 -m venv env; source env/bin/activate
pip install --upgrade pip
pip install chess
pip install -r requirements.txt

https://flask.palletsprojects.com/en/2.1.x/deploying/gunicorn/


gunicorn -w 4 -b 0.0.0.0 'hello:create_app()'
gunicorn app:server --bind=0.0.0.0:80

####
# ubuntu ec2: Steps
####

sudo apt update
sudo apt upgrade

# reboot

sudo apt install python3.10-venv
sudo apt install authbind
sudo touch /etc/authbind/byport/80
sudo chmod 500 /etc/authbind/byport/80
sudo chown ubuntu /etc/authbind/byport/80

git clone https://github.com/lineality/minimal_py_chess_mod_server.git
cd minimal_py_chess_mod_server/
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# local test
gunicorn app:app -b 0.0.0.0:8050

# aws test
authbind gunicorn app:app --bind=0.0.0.0:80
# to Run!! in background
authbind nohup gunicorn app:app --bind=0.0.0.0:80 &


# local test
python3 -m venv env; source env/bin/activate | python3 -m pip install --upgrade pip; python3 -m pip install -r requirements.txt; authbind gunicorn app:app --bind=0.0.0.0:8050

# or, safer: three parts
python3 -m venv env; source env/bin/activate

python3 -m pip install --upgrade pip; python3 -m pip install -r requirements.txt

gunicorn app:app -b 0.0.0.0:8050

notes:
1. NO paretheses in file name allowed, will fail silently and cause mayhem
2. wait: something maybe then port bind takes a few minutes
3. for debugging check pipfreeze: this can sometimes show a broken system

