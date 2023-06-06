from celery import shared_task
from celery import current_task
import requests
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

import logging
logging.basicConfig(level=logging.INFO)


channel_layer = get_channel_layer()


def send_task_update(message):
    message["task_id"] = current_task.request.id  # type: ignore
    message = json.dumps(message)
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)\
            ("tasks_updates", {"type": "websocket.send", "text": message})


@shared_task()
def ocpp_reset_task(reset_type, chargepoint_id):
    message = requests.get("http://localhost:5688/ocpp/reset/" + reset_type + "/" + chargepoint_id).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_remote_start_transaction(chargepoint_id, connector_id, id_tag, charging_profile):
    message = requests.post("http://localhost:5688/ocpp/remotestarttrasaction/" + chargepoint_id, json={"connector_id": connector_id, "id_tag": id_tag, "charging_profile": charging_profile}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_remote_stop_transaction(chargepoint_id, transaction_id):
    message = requests.post("http://localhost:5688/ocpp/remotestoptrasaction/" + chargepoint_id, json={"transaction_id": transaction_id}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_reserve_now(chargepoint_id, connector_id, id_tag, expiry_date, reservation_id):
    message = requests.post("http://localhost:5688/ocpp/reservenow/" + chargepoint_id, json={"connector_id": connector_id, "id_tag": id_tag, "expiry_date": expiry_date, "reservation_id": reservation_id}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_cancel_reservation(chargepoint_id, reservation_id):
    message = requests.post("http://localhost:5688/ocpp/cancelreservation/" + chargepoint_id, json={"reservation_id": reservation_id}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_change_availability(chargepoint_id, connector_id, availability_type):
    message = requests.post("http://localhost:5688/ocpp/changeavailability/" + chargepoint_id, json={"connector_id": connector_id, "type": availability_type}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_change_configuration(chargepoint_id, key, value):
    message = requests.post("http://localhost:5688/ocpp/changeconfiguration/" + chargepoint_id, json={"key": key, "value": value}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_clear_cache(chargepoint_id):
    message = requests.post("http://localhost:5688/ocpp/clearcache/" + chargepoint_id).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_unlock_connector(chargepoint_id, connector_id):
    message = requests.post("http://localhost:5688/ocpp/unlockconnector/" + chargepoint_id, json={"connector_id": connector_id}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp_get_configuration(chargepoint_id, keys):
    message = requests.post("http://localhost:5688/ocpp/getconfiguration/" + chargepoint_id, json={"keys": keys}).json()
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