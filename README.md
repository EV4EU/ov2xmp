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

3. Activate the environment and install the requirements
    ```sh
    $ source ./venv/bin/activate
    (venv) $ pip install -r requirements.txt
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

7. Open a new tmux session
    ```sh
    (venv) $ tmux
    ```

8. Inside the tmux session, activate the environment, and run the Django ASGI (daphne) dev server 
    ```sh
    (venv) $ python ov2xmp/manage.py runserver 0.0.0.0:8000
    ```

9. Detach from the tmux session, by pressing `CTRL + B` and `D`

10. Open a new tmux session by issuing the `tmux` command

11. Inside the new tmux session, activate the environment, and start the OCPP websocket server
    ```sh
    (venv) $ python ov2xmp/manage.py central_system_v16
    ``` 

11. If you need to record the CSMS logs to a file, issue the following instead:
    ```sh
    (venv) $ python ov2xmp/manage.py central_system_v16 2>&1 | tee central_system_output-2.log
    ```

## Deploy O-V2X-MP using docker
 
TBD
