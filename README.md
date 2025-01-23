# Open Vehicle-To-Grid Management Platform (O-V2X-MP)

[![ov2xmp-django](https://github.com/EV4EU/ov2xmp-django/actions/workflows/docker-image.yml/badge.svg)](https://github.com/EV4EU/ov2xmp-django/actions/workflows/docker-image.yml) 
  [![ov2xmp-ftp-server](https://github.com/EV4EU/ov2xmp-ftp-server/actions/workflows/docker-image.yml/badge.svg)](https://github.com/EV4EU/ov2xmp-ftp-server/actions/workflows/docker-image.yml) 
  [![ov2xmp-http-file-server](https://github.com/EV4EU/ov2xmp-http-file-server/actions/workflows/docker-image.yml/badge.svg)](https://github.com/EV4EU/ov2xmp-http-file-server/actions/workflows/docker-image.yml) 

## Citation

If you want to use this work, please cite the following paper:

```bibtex
@article{DALAMAGKAS2025102494,
title = {The Open V2X Management Platform: An intelligent charging station management system},
journal = {Information Systems},
volume = {129},
pages = {102494},
year = {2025},
issn = {0306-4379},
doi = {https://doi.org/10.1016/j.is.2024.102494},
url = {https://www.sciencedirect.com/science/article/pii/S0306437924001522},
author = {Christos Dalamagkas and V.D. Melissianos and George Papadakis and Angelos Georgakis and Vasileios-Martin Nikiforidis and Kostas Hrissagis-Chrysagis}
}
```

## Introduction

The Open Vehicle-To-Grid Management Platform (O-V2X-MP) is a set of microservices that implement the operation of a Charging Station Managment System (CSMS). The system is composed of the following microservices:

- `ov2xmp-csms`: This microservice implements the OCPP server, which establishes and manages the sessions with the EV chargers. The CSMS imports the Django ORM, so it also updates the Django database about the state of the EV charging system.
- `ov2xmp-daphne`: This is the Daphne web server, which serves the Django project and is placed as intermediate between the user and the CSMS. Django preserves the state of the system, implements high-logic, provides a RESTful API to access the system state and the CSMS-initiated OCPP commands, and enforces authentication/authorization.
- `ov2xmp-celery`: This microservice runs celery, which receives and executes tasks asynchronously.
- `ov2xmp-postgres` provides the persistent storage for Django.
- `ov2xmp-ftp-server`: This microservice is a custom FTP server that provides access for EV chargers to upload files via FTP to the `filebrowser-root` docker volume. The source code of this project is a git submodule of the main (`ov2xmp`) repo.
- `ov2xmp-http-file-server`: This microservice is a custom HTTP server that allows EV chargers to upload or download files via HTTP to/from the `filebrowser-root` docker volume. The source code of this project is a git submodule of the main (`ov2xmp`) repo.
- `ov2xmp-filebrowser`: Based on the [[filebrowser.org]] project, it provides a user-friendly GUI for the user to access the contents of the `filebrowser-root` docker volume and download/upload files manually.
- `ov2xmp-caddy` acts as the reverse proxy and TLS termination proxy of O-V2X-MP.
- `ov2xmp-pgadmin4` is a GUI for managing the `ov2xmp-postgres`.
- `ov2xmp-portainer` is a GUI for managing the docker containers.
- `ov2xmp-redis` is the backend for Django to support Django Channels. Through Django Channels, the Django backend can transmit data asynchronously to the frontend via WebSockets.

> Please note that the `ov2xmp-daphne`, `ov2xmp-csms` and `ov2xmp-celery` microservices are deployed from the same `ov2xmp-django` git submodule of the `ov2xmp` repo.

## Configuration of the O-V2X-MP microservices

### ov2xmp-filebrowser

The `filebrowser.json` configuration file must be placed inside the `filebrowser` folder with the following content:

```json
{
    "port": 80,
    "baseURL": "/filebrowser",
    "address": "",
    "log": "stdout",
    "database": "/database/filebrowser.db",
    "root": "/srv"
}
```

### ov2xmp-ftp-server

The `config.json` configuration file must be placed inside the `ftp-server` folder with the following content:

```json
{
    "username": "The username used by the EV charger to upload files",
    "password": "The password of the user account"
}
```

The following URL must be provided to an EV charger that needs to access the FTP server:

`ftp://<username>:<password>@<OV2XMP_Address>/files`

Where:

- `<username>` must be replaced with the username specified in `config.json`.
- `<password>` must be replaced with the password specified in `config.json`.
- `<OV2XMP_Address>` must be replaced with the IP address of the FQDN of OV2XMP.

### ov2xmp-http-file-server

The `config.json` configuration file must be placed inside the `http-file-server` folder with the following content:

```json
{
    "username": "The username used by the EV charger to upload files",
    "password": "The password of the user account"
}
```

The following URL must be provided to an EV charger that needs to access the HTTP server:

`http://<username>:<password>@<OV2XMP_Address>/http/upload/`

Where:

- `<username>` must be replaced with the username specified in `config.json`.
- `<password>` must be replaced with the password specified in `config.json`.
- `<OV2XMP_Address>` must be replaced with the IP address of the FQDN of OV2XMP.

### ov2xmp-caddy

The Caddy server consists of three configuration files:

- `caddyfile-base` contains all the configuration directives that apply under any circumstances.
- `caddyfile-dev` imports `caddyfile-base` and is appropriate for development and staging, since it requires a local FQDN and the usage of self-signed certificates. This version requires the `CADDY_PUBLIC_FQDN` env. variable to be set.
- `caddyfile-prod` imports `caddyfile-base` and is suitable for production usage, requiring to specify a public FQDN that LetsEncrypt can use to obtain valid certificates. This version requires the `CADDY_PUBLIC_FQDN` env. variable to be set.

### ov2xmp-daphne, ov2xmp-csms and ov2xmp-celery

Check the `README.md` in the `ov2xmp-django` submodule.

### ov2xmp-postgres

The `.env` file must be placed inside the `postgres` folder with the following content:

```env
POSTGRES_DB=ov2xmp
POSTGRES_USER=ev4eu
POSTGRES_PASSWORD=XXXX
```

> Make sure that the contents of this `.env` file match the postgres info specified in the corresponding `.env` file of `ov2xmp-django`.

### ELK stack

Optionally, the ELK stack can be deploying alongside with O-V2X-MP, in order to manage and organise the various logs. To deploy the ELK stack, the following components should be deployed, which are located in the `docker-compose-externals.yml`:
- `ov2xmp-logstash` receives and handles the logs from the `ov2xmp-csms` and `ov2xmp-daphne` services (processing, formatting, output to one or multiple destinations).
- `ov2xmp-elasticsearch` can store the various system logs received by Logstash.
- `ov2xmp-elasticsearch-setup` initiates the password of the `kibana_system` user (is executed only once and terminates).
- `ov2xmp-kibana` is the GUI for managing the elasticsearch instance.

For elasticsearch, the `.env-es` file and the `elasticsearch.yml` files are used.

For kibana, the `.env-kibana` file is used.

For logstash, the `.env-logstash` file is used for configuration, while the `ov2xmp-normalizer.conf` specifies the logstash pipeline. The latter is developer alongside OV2XMP and depends on the log format and its variations adopted by the log producers.

Finally, `ov2xmp-elasticsearch-setup` utilises the `elk-setup.sh` script, which initialises the `kibana_system` user in elasticsearch.

## O-V2X-MP Deployment

GitHub Actions have been configured for all submodules with custom code, i.e. `ov2xmp-django`, `ov2xmp-ftp-server` and `ov2xmp-http-file-server`. For each commit pushed to the main branch of any of these submodules, the CI pipeline is triggered automatically to produce a docker image, which is uploaded to the GitHub docker registry.

However, it is preferable sometimes to test the integrated docker images without pushing commits to the main branch. Fpr this purpose, there are three kinds of deployment:

- **dev**: This setup deploys only the infrastructure docker containers (all `ov2xmp-*` containers, except `ov2xmp-daphne`, `ov2xmp-csms` and `ov2xmp-celery`). Django, CSMS and Celery are deployed manually from source code on the development VM, using the command line. This deployment is prefered during development and testing, since the new code can be immediately tested. For this deployment, `.env-local` is loaded manually by the developer to configure Django.
- **staging**: This setup replicates the production deployment, however, local docker images are used instead of those stored in the GitHub docker registry. Moreover, the TLS termination proxy (caddy) uses self-signed certificates. The idea behind this deployment is that the developer may need to test the integrated version of `ov2xmp-daphne`, `ov2xmp-csms` and `ov2xmp-celery` before commiting the changes and pushing to the GitHub repo.
- **production**: This is the production deployment which uses the official docker images that are available in the GitHub repo. Moreover, it assumes that valid certificates are used, so `ov2xmp-caddy` should be pointed to a public domain.

### Deploy O-V2X-MP in development environment

1. Ensure that the configuration of all O-V2X-MP modules is correct.
2. Check the `.env-local` file of `ov2xmp-django`.
3. Deploy the infrastructure docker containers with:

   ```sh
   docker-compose -f docker-compose-dev.yml up -d
   ```

4. Check the `ov2xmp-django/README.md` file for instructions to deploy from source code.

### Deploy O-V2X-MP in stage environment

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
docker-compose -f docker-compose-staging.yml up -d
```

### Deploy O-V2X-MP in production

To deploy in production, login to the GitHub container registry and use the corresponding docker-compose file:

```sh
docker login ghcr.io -u USERNAME
docker-compose -f docker-compose-prod.yml up -d
```

## Accessing the O-V2X-MP REST API

The O-V2X-MP can be accessed through the following URL:

> `https://{OV2XMP_FQDN}/api/`

Replace `{OV2XMP_FQDN}` with the valid FQDN of the platform. For example, it could be a public FQDN (`ov2xmp.trsc-ppc.gr`) if you are using the production deployment, or a local FQDN (`ov2xmp.trsc.net`) if you are using a local staging instance.

All API requests must be authenticated by using a valid JSON Web Token (JWT). To get a JWT for your account, follow these steps:

1. Scroll down to the `/api/token` request or visit the following URL: `https://{OV2XMP_FQDN}/api/#/token/token_create`.

2. Click on `Try it out`.

3. Inside the Request body, replace the values of `username` and `password` with the credentials provided to you for O-V2X-MP.

4. Click on `Execute`.

5. Scroll down a bit and copy the Response body. Inside the response, there is a refresh token and an access token. The access token is the authentication token whereas the refresh token can be used to renew the validity of the access token through the `/api/token/refresh/` endpoint.

6. Scroll at the top of the Swagger page and click on the `Authorize` button.

7. Paste the access token as the value of the `jwtAuth` authorization.

8. Now, all requests made through the page are automatically authorized.


## Connecting EV Charging Stations

### Production and Staging mode

In order to connect an EV charger to O-V2X-MP, you need to provide the following connection URL to the EV charger:

> `ws://{OV2XMP_FQDN}/ws/ocpp`

Replace `{OV2XMP_FQDN}` with the valid FQDN of the platform. For example, it could be a public FQDN (`ov2xmp.trsc-ppc.gr`) if you are using the production deployment, or a local FQDN (`ov2xmp.trsc.net`) if you are using a local staging instance.

### Development mode

If the CSMS is deployed in development mode (i.e., directly from the source code), you need to specify the TCP port of the CSMS in the URL. So the URL should be something like this:

> `ws://{OV2XMP_ADDRESS}:9000/ws/ocpp`

Replace `{OV2XMP_ADDRESS}` with the local FQDN **OR** the IP address of the VM where the O-V2X-MP platform runs.


## Integration with Frontend

Due to the microservice architecture of O-V2X-MP, it can be easily integrated with any frontend microservice (e.g., a docker container running Vue.js or similar).

To accomplish this, you should edit the `caddyfile-base` configuration file of caddy, and specify the target of the `reverse_proxy * ` directive. For example, provide `reverse_proxy * 192.168.21.25:5173` at the end of the file, if the frontend service is at 192.168.21.25 and listens to port 5173.