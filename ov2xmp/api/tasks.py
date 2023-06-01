from celery import shared_task
from celery import current_task
import requests
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


channel_layer = get_channel_layer()


def send_task_update(message):
    message["task_id"] = current_task.request.id  # type: ignore
    message = json.dumps(message)
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)\
            ("tasks_updates", {"type": "websocket.send", "text": message})


@shared_task()
def ocpp_reset_task(reset_type, chargepoint_url_identity):
    message = requests.get("http://localhost:5688/ocpp/reset/" + reset_type + "/" + chargepoint_url_identity).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_remote_start_transaction(chargepoint_url_identity, connector_id, id_tag, charging_profile):
    message = requests.post("http://localhost:5688/ocpp/remotestarttrasaction/" + chargepoint_url_identity, json={"connector_id": connector_id, "id_tag": id_tag, "charging_profile": charging_profile}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_remote_stop_transaction(chargepoint_url_identity, transaction_id):
    message = requests.post("http://localhost:5688/ocpp/remotestoptrasaction/" + chargepoint_url_identity, json={"transaction_id": transaction_id}).json()
    send_task_update(message)
    return message


'''
@shared_task()
def dummy_task(param1, param2):
    time.sleep(5)
    message = {
        "success": True,
        "message": "Task completed",
    }
    send_task_update(message)
    return message
'''