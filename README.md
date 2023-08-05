# Open Vehicle-To-Grid Management Platform (O-V2X-MP)

The Open Vehicle-To-Grid Management Platform (O-V2X-MP) is a set of micro-services that implement the operation of a Charging Station Managment System (CSMS). The system is composed of the following microservices:+

- `ov2xmp-django`: The main microservice of O-V2X-MP, that integrates a Django server and the OCPP server. The OCPP server implements all the OCPP operations according to OCPP 1.6 and 2.0.1, while the Django server implements high-logic, provides a RESTful API, enforces authentication/authorization, and provides persistent storage for the state of the EV charging infrastructure.
- `ftp-server`: This microservice is a custom FTP server that provides access for EV chargers to upload files via FTP to the `filebrowser-root` docker volume.
- `http-file-server`: This microservice is a custom HTTP server that allows EV chargers to upload or download files via HTTP to/from the `filebrowser-root` docker volume.
- `filebrowser`: Based on the [[filebrowser.org]] project, it provides a user-friendly GUI for the user to access the contents of the `filebrowser-root` docker volume and download/upload files manually.
- `nginx` acts as the reverse proxy and TLS termination proxy of O-V2X-MP. Currently, only `ov2xmp`
- `postgres` provides the persistent storage for Django.

## OV2XMP submodules

### filebrowser

The `filebrowser.json` configuration file must be placed inside the `filebrowser` folder with the following content:

```json
{
    "port": 80,
    "baseURL": "",
    "address": "",
    "log": "stdout",
    "database": "/database/filebrowser.db",
    "root": "/srv"
}
```

### ftp-server

The `config.json` configuration file must be placed inside the `ftp-server` folder with the following content:

```json
{
    "username": "The username used by the EV charger to upload files",
    "password": "The password of the user account"
}
```

### http-file-server

The `config.json` configuration file must be placed inside the `http-file-server` folder with the following content:

```json
{
    "username": "The username used by the EV charger to upload files",
    "password": "The password of the user account"
}
```

### nginx

A folder named `tls` must be placed inside the `nginx` folder. The `tls` folder must contain a TLS certificate and TLS key to be used by nginx for TLS proxying.

Moreover, a file named `nginx.conf` must be placed inside the `nginx` folder, with the following content:

```nginx
user nginx;
worker_processes auto;
pcre_jit on;
error_log /var/log/nginx/error.log warn;
include /etc/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    resolver 127.0.0.11 ipv6=off;
    server_tokens off;
    client_max_body_size 1m;
    keepalive_timeout 65;
    sendfile on;
    tcp_nodelay on;

    gzip on;
    gzip_vary on;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
            '$status $body_bytes_sent "$http_referer" '
            '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    server {
        listen       80 default_server;
        server_name  _;

        return 301 https://$host$request_uri;

        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }
    }

    server {
        listen 443 ssl;

        server_name _;

        ssl_certificate /etc/nginx/tls/cert.pem;
        ssl_certificate_key /etc/nginx/tls/key.pem;

        location / {
            proxy_pass http://ov2xmp-django:8000;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;
            proxy_redirect off;
        }

        location /static {
            alias /code/static;
        }

        location /media {
            alias /code/media;
        }

    }
}
```

### ov2xmp-django

Check the `README.md` in the `ov2xmp-django` submodule.

## postgres

The `.env` file must be placed inside the `postgres` folder with the following content:

```env
POSTGRES_DB=ov2xmp
POSTGRES_USER=ev4eu
POSTGRES_PASSWORD=XXXX
```

## Deployment

Gitlab CI/CD has been configured for all submodules with custom code, i.e. `ov2xmp-django`, `ftp-server` and `http-file-server`. For each commit pushed to the main branch of any of these submodules, the CI pipeline is triggered automatically to produce a docker image, which is uploaded to the Gitlab docker registry.

However, it is preferable sometimes to test the integrated docker images without pushing commits to the main branch. For these kind of tests (staging), the developer can build the docker image using the Dockerfiles, save the images on their machine and deploy them locally on a stage environment for testing.

### Deploy O-V2X-MP in stage environment

Deployment in staging mode assumes the usage of the local docker images, instead of those stored in the Gitlab registry. To deploy in a stage environment, follow the steps bellow:

1. Enter the `ftp-server` directory and build the docker image.

    ```sh
    cd ftp-server
    docker build -t ov2xmp-ftp-server .
    ```

2. Enter the `http-file-server` directory and build the docker image.

    ```sh
    cd http-file-server
    docker build -t ov2xmp-http-file-server .
    ```

3. Enter the `ov2xmp-django` directory and build the docker image.

    ```sh
    cd ov2xmp-django
    docker build -t ov2xmp-django .
    ```

4. Deploy using the following command:

```sh
docker-compose -f docker-compose-dev.yml up -d
```

### Deploy O-V2X-MP in production

The main difference in production is that the docker images are already available in the Gitlab registry.

To deploy in production, use the corresponding docker-compose file:

```sh
docker-compose -f docker-compose-dev.yml up -d
```
