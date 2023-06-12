# Open Vehicle-To-Grid Management Platform (O-V2X-MP)

## Deploy O-V2X-MP from source code

1. Clone the project

    ```shell
    git clone https://gitlab.trsc-ppc.gr/ev4eu/o-v2x-mp
    ```

2. Create a Python virtual environment

    ```sh
    cd o-v2x-mp
    python3 -m venv venv
    ```

3. Activate the environment and install the requirements. Install also the prerequisites needed to build the `python-ldap` library.

    ```sh
    $ source ./venv/bin/activate
    (venv) $ pip install -r requirements.txt
    $ apt install gcc libldap2-dev libsasl2-dev ldap-utils
    ```

4. Migrate

    ```sh
    (venv) $ python ov2xmp/manage.py migrate
    ```

5. Create a superuser

    ```sh
    (venv) $ python ov2xmp/manage.py createsuperuser
    ```

6. Go inside the ov2xmp folder and open a new tmux session

    ```sh
    (venv) $ cd ov2xmp
    (venv) $ tmux
    ```

7. Inside the tmux session, activate the environment, and run the Django ASGI (daphne) dev server

    ```sh
    $ source ../venv/bin/activate
    (venv) $ python manage.py runserver 0.0.0.0:8000
    ```

    Detach from the tmux session, by pressing `CTRL + B` and `D`.

8. Open a new tmux session by issuing the `tmux` command. Inside the new tmux session, activate the environment, and start the OCPP websocket server

    ```sh
    (venv) $ python manage.py central_system_v16
    ```

    Alternatively, if you need to record the CSMS logs to a file, issue the following instead:

    ```sh
    (venv) $ python manage.py central_system_v16 2>&1 | tee central_system_output-2.log
    ```

9. Open a new tmux session by issuing the `tmux` command, and start the Celery worker:

    ```sh
    $ source ../venv/bin/activate
    (venv) $ celery -A ov2xmp worker -l info
    ```

10. Open a new tmux session by issuing the `tmux` command, and start the Celery Flower module:

    ```sh
    $ source ../venv/bin/activate
    (venv) $ celery -A ov2xmp flower
    ```

## Overview of task management pipeline for OCPP requests

In summary, in order for someone to initiate a synchronous request to the O-V2X-MP for an underlying EVCS (i.e., if `sync` is set to `true`):

```plantuml
@startuml
actor user as "User app"
participant ov2xmp as "OV2XMP \nREST API"
entity celery as "Celery Task"
participant csms as "CSMS \nREST API"
entity cp as "ChargePoint\n (mobilityhouse)"

user -> ov2xmp : REST API request
activate user
ov2xmp -> celery : Call task \nfunction
celery -> csms : REST API call
csms -> cp : Call method
cp -> csms : Call resonse
csms -> celery : REST API \nresponse
celery -> ov2xmp : Call response
ov2xmp -> user : REST API \nresponse
deactivate user
@enduml
```

In case of an asynchronous request (i.e., if `sync` is set to the default value (`false`):

```plantuml
@startuml
actor user as "User app"
participant ov2xmp as "OV2XMP \nREST API"
entity celery as "Celery Task"
participant csms as "CSMS \nREST API"
entity cp as "ChargePoint\n (mobilityhouse)"

user -> ov2xmp : REST API call
activate user
ov2xmp -> celery : submit task
celery -> ov2xmp : task ID
activate celery
ov2xmp -> user : task ID
deactivate user
celery -> csms : REST API call
csms -> cp : Call method
cp -> csms : Call resonse
csms -> celery : REST API \nresponse
celery -> celery : Update task \nstatus
user -> ov2xmp : Request task status
activate user
ov2xmp -> celery : Request task status
celery -> ov2xmp : Task status
ov2xmp -> user : Task status
deactivate user
@enduml
```

## How to develop REST API endpoints for OCPP commands

To implement a REST API endpoint for issuing an OCPP v1.6 command that is initiated by the CSMS (e.g., a Reset command), follow the steps bellow:

1. First, we have to define the function that implements the entire logic of the command, from scratch. In particular, inside `dashboard/management/commands/central_system_v16.py`, under the "ACTIONS INITIATED BY THE CSMS" comment header, create a function for the ChargePoint class, like this:

    ```python
    # Reset
    async def reset(self, reset_type):
        request = call.ResetPayload(type = reset_type)
        response = await self.call(request)
        if response is not None:
            return {"status": response.status}
        else:
            return {"status": None}
    ```

    Some notes:

    - Start with a comment that refers to the OCPP command name
    - The function must be async.
    - The function parameters can be determined by checking the corresponding class inside `ocpp.v16.call`. For the Reset command, the parameters are derived from the `ResetPayload` class. This class has the `type` attribute, therefore we define the corresponding argument.
    - Inside the function, we define the entire logic of the OCPP command and make all the Django ORM calls. Note that in the end we must return a specific dictionary: `{"status": XXX}`, where `XXX` is whatever output we need to return.

2. Next, we have to add a REST API endpoint to the Flask server of the CSMS (this is utilised by Django to initiate actions towards the OCPP server and the ChargePoint objects). In particular, under the CSMS REST API comment section of the `dashboard/management/commands/central_system_v16.py` file, create a new function, like this:

    ```python
    # Reset (hard or soft)
    @app.route("/ocpp/reset/<chargepoint_id>", methods=["POST"])
    async def reset(chargepoint_id):
        if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
            resetType = request.json["reset_type"]
            result = await CHARGEPOINTS_V16[chargepoint_id].reset(resetType)
            return jsonify(result)
        else:
            return jsonify({"status": "Charge Point does not exist"})

    ```

    Some notes:
    - Start with a comment that refers to the OCPP command name
    - The `@app.route()` decorator defines the URL of the new OCPP command. It must follow the following format: `/ocpp/XXX/<chargepoint_id>`, where `XXX` is the name of the OCPP command. Always the method is POST and all parameters are provided in the JSON payload, except the `chargepoint_id`, which is defined in the URL.
    - At the beginning, the check `if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None` is always performed. If successful, the parameters are extracted from `request.json` and the corresponding function that we implemented in step 1 is called.

3. Next, create a celery task that calls the REST API endpoint previously defined. To do that, define a function inside `api/tasks.py` like this:

    ```python
    @shared_task()
    def ocpp_reset_task(chargepoint_id, reset_type):
        message = requests.post("http://localhost:5688/ocpp/reset/" + chargepoint_id, json={"reset_type": reset_type}).json()
        send_task_update(message)
        return message
    ```

    Some notes:
    - It always start with the `@shared_task()` decorator.
    - Note the function name. It starts with `ocpp_`, then the OCPP command name follows, and it ends with `_task`.
    - All command parameters are provided in the function arguments (e.g., `reset_type`)
    - Command parameters are transfered to the CSMS service via the `json` argument of the `requests.post()` function.
    - At the end, the command respond is provided to the `send_task_update()`, which broadcasts the results via Django Channels.

    > Please note that after changing `tasks.py`, you need to restart the celery worker in order for the changes to take effect.

4. Next, we can start by defining the external REST API endpoint exposed by the Django system (OpenAPI). To do this, start by defining the serializer in `api/serializers.py`. In this file, create a serializer for the endpoint, like the following:

    ```python
    class OcppResetSerializer(OcppCommandSerializer):
        reset_type = serializers.ChoiceField(choices=tuple(member.value for member in ocppv16_enums.ResetType))
    ```

    Some notes:
    - Note the class name. It starts with `Ocpp`, then the OCPP commmand follows, and it ends with `Serializer`.
    - It inherits the `OcppCommandSerializer`, which defines the parameters that are accepted by all OCPP commands. In particular, all OCPP commands must accept the `chargepoint_id` and the `sync` parameter.
    - The new serializer needs to define only the extra parameters that are associated with the corresponding OCPP command.

5. Next, define the API View inside `api/views.py` like the following:

    ```python
    class OcppResetApiView(GenericAPIView):
        permission_classes = [permissions.IsAuthenticated]
        serializer_class = OcppResetSerializer
        schema = AutoSchema(tags=['OCPP'])

        def post(self, request, *args, **kwargs):
            '''
            Send a Reset command (hard or soft)
            '''

            serializer = OcppResetSerializer(data=request.data)
            if serializer.is_valid():
                if serializer.data["sync"]:
                    task = ocpp_reset_task(serializer.data["chargepoint_id"], serializer.data["reset_type"])
                    task["success"] = True
                    return Response(task, status=status.HTTP_200_OK)
                else:
                    task = ocpp_reset_task.delay(serializer.data["chargepoint_id"], serializer.data["reset_type"]) # type: ignore
                    return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    ```

    Some notes:
    - Keep the above structure/logic
    - Replace the serializer `serializer_class`
    - Its important to provide a command description in the comment under the `post()` function (this comment is parsed in order to automatically generate the OpenAPI spec).
    - In `serializer = OcppResetSerializer(data=request.data)` replace the serializer with your's
    - Inside the `if serializer.data["sync"]:` statement, replace the task function and its corresponding parameters.

6. Include the new endpoint in `api/urls.py`, like so:

    ```python
    path('ocpp/reset/', OcppResetApiView.as_view()),
    ```

    Some notes:
    - In `ocpp/reset/`, replace `reset` with the command name
    - Replace `OcppResetApiView` with the name of the API view class defined previously.
