# Django Face Rcognition Service

latest updates on:
https://github.com/parsadany/django_face_recognition_service

This project is built to deploy easily and consume by apis.

## Deploy:
you have two ways to deploy:

### linux service:

0. prepare your postgres database and create a file ```.env``` including your database connection.

```
Environment=PROD
DATABASE_ENGINE=postgresql_psycopg2
DATABASE_NAME=dbname
DATABASE_USERNAME=username
DATABASE_PASSWORD='password'
DATABASE_HOST='127.0.0.1'
DATABASE_PORT=1234
CORS_URLS='' # see the settings.py to customize!
```

after all, you should put this file beside the manage.py file.

1. Prepare a linux server with python3 installed.

2. prepare your domains and dns configurations to point to the server.

3. get ssh access to the server.

4. clone the project somewhere for example:
```
git clone https://github.com/parsadany/django_face_recognition_service.git /app/face_recognition/.
```

5. create virtual environment and initialize installation of packages.

```
cd /app/face_recognition/
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

6. ```nano /etc/nginx/sites-available/django_face_recognition.conf```
then paste this into it and change the server_name to what you want.
```
upstream facerecognitionapi {
        server unix:/run/facerecognitionapi.sock;
}
server {
        access_log /var/log/nginx/facerecognitionapi.access.log;
        error_log /var/log/nginx/facerecognitionapi.error.log;
        server_name face.example.com;
        charset     utf-8;
        client_max_body_size 30M;
        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
                alias /home/;
                try_files /$uri $uri/ =404;
        }
        # location /media/ {
        #        alias /home/;
        #        try_files /$uri $uri/ =404;
        # }
        location / {
                proxy_pass http://facerecognitionapi;
                include proxy_params;
                proxy_redirect off;
        }
}
```
to save and exit :
ctrl + x -> y -> enter

7. create a socket for your project. ```nano /lib/systemd/system/facerecognitionapi.socket``` then pathe this content in it:

```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/facerecognitionapi.sock
# Our service won't need permissions for the socket, since it
# inherits the file descriptor by socket activation
# only the nginx daemon will need access to the socket
User=root
# Optionally restrict the socket permissions even more.
# Mode=600

[Install]
WantedBy=sockets.target

```
to save and exit :
ctrl + x -> y -> enter

8. create a service for this socket. ```nano /lib/systemd/system/facerecognitionapi.service``` then copy the content in it and change the /path/to/cloned/project:
```
[Unit]
Description=gunicorn daemon
Requires=facerecognitionapi.socket
After=network.target

[Service]
Type=notify
# the specific user that our service will run as
#User=someuser
#Group=someuser
# another option for an even more restricted service is
# DynamicUser=yes
# see http://0pointer.net/blog/dynamic-users-with-systemd.html
RuntimeDirectory=backend
WorkingDirectory=/path/to/cloned/project # could be /app/face_recognition/
ExecStart=/path/to/cloned/project/venv/bin/gunicorn face_recognition.wsgi:application -w 1 # could be /app/face_recognition/venv/bin/gunicorn
#path_to_virtualenv_gunicorn_module --pythonic_path_to_wsgi_module -w $number_of_workers
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

9. restart daemon: ```systemctl daemon-reload```

10. start and enable services with tests:

```
nginx -t
systemctl enable facerecognitionapi.socket
systemctl enable facerecognitionapi.service
systemctl start facerecognitionapi.socket
systemctl start facerecognitionapi.service
systemctl reload nginx
```

### Dockerized:

copy this content to your docker-compose.yml file in your server. so you will be able to run all services including postgres and nginx or just run the service that you need.
you also need to copy the nginx configuration.

in case that you want to run many things behind the nginx on a single server, the port 80 and 443 will be captured by nginx container. so you can install an nginx on your server and set a reverse proxy up to other containers and services. in this method, the port 80 is only captured by a global nginx service.

```nano /app/dockerized_face_recognition/docker-compose.yml```

then copy this into it:

# this is beta samples, todo!
```
version: '3.8'

services:
  web:
    build:
      context: ./app
      dockerfile: Dockerfile.prod
    command: gunicorn hello_django.wsgi:application --bind 0.0.0.0:8686
    volumes:
      - static_volume:/home/app/web/staticfiles
    expose:
      - 8686
    env_file:
      - ./.env.prod
    depends_on:
      - db
  db:
    image: postgres:13.0-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - ./.env.prod.db
  nginx:
    build: ./nginx
    volumes:
      - static_volume:/home/app/web/staticfiles
    ports:
      - 1337:80
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
```