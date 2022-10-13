# m.a.t. pychess nginx

binding to port 80 is done with simpler manual ngix configuration

18.234.222.205

```
hybrid ec2 install use these methods mixed:

https://lcalcagni.medium.com/deploy-your-fastapi-to-aws-ec2-using-nginx-aa8aa0d85ec7 

https://berkoc.medium.com/how-to-deploy-your-flask-app-to-aws-ec2-instance-with-nginx-gunicorn-b734df606a14

ubuntu
https://towardsdatascience.com/deploy-multiple-flask-applications-using-nginx-and-gunicorn-16f8f7865497 

yum
https://medium.com/sai-ops/installing-nginx-using-aws-ec2-user-data-5590fdbe528d
hybrid ec2 install use these methods mixed:

Good!
https://lcalcagni.medium.com/deploy-your-fastapi-to-aws-ec2-using-nginx-aa8aa0d85ec7 

only some bits
https://berkoc.medium.com/how-to-deploy-your-flask-app-to-aws-ec2-instance-with-nginx-gunicorn-b734df606a14

only some bits
https://towardsdatascience.com/deploy-multiple-flask-applications-using-nginx-and-gunicorn-16f8f7865497 

must have: https://www.youtube.com/watch?v=JQP96EjRM98 
```


## mod of pip install chess
```
m Modular

a Amnesiac

t Turnbased
```
m.a.t. gaming system

- endpoint oriented


///////////////////////////////////////////////////////////////

debugging:
```
make env
$ python3
$ import chess, mat_chess
$ 
```

//////////////////////////////////////////////////////////


python3 -m venv env; source env/bin/activate
pip install --upgrade pip
pip install chess
pip install -r requirements.txt

https://flask.palletsprojects.com/en/2.1.x/deploying/gunicorn/


gunicorn -w 4 -b 0.0.0.0 'hello:create_app()'
gunicorn app:server --bind=0.0.0.0:80


# local env test (before deploy)
### safer: three parts
```
python3 -m venv env; source env/bin/activate

python3 -m pip install --upgrade pip; python3 -m pip install -r requirements.txt

gunicorn app:app
```

####
# ubuntu ec2: Steps
####


### From Github:
```
sudo apt update -y; sudo apt upgrade -y

# reboot

sudo apt install python3-pip python3.10-venv nginx -y

git clone https://github.com/lineality/minimal_py_chess_mod_server.git

cd minimal_py_chess_mod_server/

python3 -m venv env; source env/bin/activate

python3 -m pip install --upgrade pip; python3 -m pip install -r requirements.txt

```
##### or

### Done Manually
```
sudo apt update -y; sudo apt upgrade -y

# reboot

sudo apt install python3-pip python3.10-venv nginx -y

mkdir matgames; cd matgames

python3 -m venv env; source env/bin/activate

python3 -m pip install --upgrade pip; python3 -m pip install flask gunicorn python-dotenv chess
```

### Check / Change the port to 80
```
nano app.py

last line ->     app.run_server
```

### Check / Change the image file URL in HTML files
```
nano templates/NAME_OF_GAME.html 

line 18 ->           <img src="http://18.234.222.205/tyrell_board" alt="smile" height="850px" width="850px" />
should be ec2 url
```

### local test (no bind, or bind to generic)
```
gunicorn app:app

to here even without binding??
http://127.0.0.1:8000

gunicorn --bind 0.0.0.0:8050 app_test:app
gunicorn --bind 127.0.0.1:8000 app_test:app
gunicorn --bind 127.0.0.1:8000 app:app
```

###  to Run!! in background, run to debug without this so you can see output?
```
nohup gunicorn --bind 127.0.0.1:8000 app:app &
```

## notes:
1. NO paretheses in file name allowed, will fail silently and cause mayhem
2. wait: something maybe then port bind takes a few minutes
3. for debugging check pipfreeze: this can sometimes show a broken system
4. maybe another-another server is needed for tie port 80 to wsgi...
5. maybe test on port 80 before having run in background



##########
# ubuntu
##########

## sites ports and listening

By default, Nginx contains one server block called default. 
You can find it in this location: 
```
sudo nano etc/nginx/sites-enabled/default
```

But we will create a new one called “nginx” (you can choose another name):

cd /etc/nginx/sites-enabled/

sudo nano nginx

### make 
```
server {    
    listen 80;    
    server_name YOUR_PUBLIC_EC2_ADDRESS;    

    location / {        
    proxy_pass http://127.0.0.1:8000;
    }
}
```



# SSL self signed
```
sudo apt-get install openssl

cd /etc/nginx

sudo mkdir ssl

sudo openssl req -batch -x509 -nodes -days 365 -newkey rsa:2048 -keyout etc/nginx/ssl/server.key -out /etc/nginx/ssl/server.crt
```



## Go To:
```
sudo nano /etc/nginx/sites-enabled/nginx
```

## make:
#### maybe find a way to put the AWS cert data in here...
```
server {
    listen 80;
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    server_name 18.234.222.205;
    
        location / {
            proxy_pass http://127.0.0.1:8000;
    }
    }
```
on chrome this works to connect to HTTPS, but you will get a self-signed warning

## activate with
```
sudo systemctl start nginx.service
sudo systemctl enable nginx.service
```

# check with
```
sudo systemctl status nginx.service -l
sudo journalctl -xeu nginx.service
```

#remove!
## remove 
```
/etc/nginx/sites-enabled/default

cd /etc/nginx/sites-enabled/
sudo rm default
```

# Restart nginx
```
sudo service nginx restart
```

Then run your app manually in back ground, e.g. with nohup ... &

