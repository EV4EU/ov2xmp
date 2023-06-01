# Open Vehicle-To-Grid Management Platform (O-V2X-MP)

## Deploy O-V2X-MP from source code

1. Clone the project
    ```sh
    $ git clone https://gitlab.trsc-ppc.gr/ev4eu/o-v2x-mp
    ```

2. Create a Python virtual environment
    ```sh
    $ cd o-v2x-mp
    $ python3 -m venv venv
    ```

3. Activate the environment and install the requirements. Install also the prerequisites needed to build the `python-ldap` library.
    ```sh
    $ source ./venv/bin/activate
    (venv) $ pip install -r requirements.txt
    $ apt install gcc libldap2-dev libsasl2-dev ldap-utils
    ```

4. **SKIP THIS FOR NOW** - Deploy the database
    ```sh
    $ docker-compose -f docker-compose-db.yml up -d
    ```

5. Migrate
    ```sh
    (venv) $ python ov2xmp/manage.py migrate
    ```

6. Create a superuser
    ```sh
    (venv) $ python ov2xmp/manage.py createsuperuser
    ```

7. Go inside the ov2xmp folder and open a new tmux session
    ```sh
    (venv) $ cd ov2xmp
    (venv) $ tmux
    ```

8. Inside the tmux session, activate the environment, and run the Django ASGI (daphne) dev server 
    ```sh
    $ source ../venv/bin/activate
    (venv) $ python manage.py runserver 0.0.0.0:8000
    ```
    Detach from the tmux session, by pressing `CTRL + B` and `D`.

9. Open a new tmux session by issuing the `tmux` command. Inside the new tmux session, activate the environment, and start the OCPP websocket server
    ```sh
    (venv) $ python manage.py central_system_v16
    ``` 

    Alternatively, if you need to record the CSMS logs to a file, issue the following instead:
    ```sh
    (venv) $ python manage.py central_system_v16 2>&1 | tee central_system_output-2.log
    ```

10. Open a new tmux session by issuing the `tmux` command, and start the Celery worker:
    ```sh
    $ source ../venv/bin/activate
    (venv) $ celery -A ov2xmp worker -l info
    ```

11. Open a new tmux session by issuing the `tmux` command, and start the Celery Flower module:
    ```sh
    $ source ../venv/bin/activate
    (venv) $ celery -A ov2xmp flower
    ```


## Deploy O-V2X-MP using docker
 
TBD
