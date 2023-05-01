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

4. Deploy the database
    ```sh
    $ docker-compose -f docker-compose-db.yml up -d
    ```

5. Migrate
    ```sh
    (venv) $ python ov2xmp/manage.py migrate
    ```

6. Run the dev server 
    ```sh
    (venv) $ python ov2xmp/manage.py runserver 0.0.0.0
    ```

7. Create a superuser
    ```sh
    (venv) $ python ov2xmp/manage.py createsuperuser
    ```


## Deploy O-V2X-MP using docker
 
TBD
