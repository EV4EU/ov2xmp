from celery import shared_task
from celery import current_task
import requests
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
def ocpp16_reset_task(chargepoint_id, reset_type):
    message = requests.post("http://localhost:9000/ocpp16/reset/" + chargepoint_id, json={"reset_type": reset_type}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_remote_start_transaction(chargepoint_id, connector_id, id_tag, charging_profile):
    message = requests.post("http://localhost:9000/ocpp16/remotestarttransaction/" + chargepoint_id, json={"connector_id": connector_id, "id_tag": id_tag, "charging_profile": charging_profile}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_remote_stop_transaction(chargepoint_id, transaction_id):
    message = requests.post("http://localhost:9000/ocpp16/remotestoptransaction/" + chargepoint_id, json={"transaction_id": transaction_id}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_reserve_now(chargepoint_id, connector_id, id_tag, expiry_date, reservation_id):
    message = requests.post("http://localhost:9000/ocpp16/reservenow/" + chargepoint_id, json={"connector_id": connector_id, "id_tag": id_tag, "expiry_date": expiry_date, "reservation_id": reservation_id}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_cancel_reservation(chargepoint_id, reservation_id):
    message = requests.post("http://localhost:9000/ocpp16/cancelreservation/" + chargepoint_id, json={"reservation_id": reservation_id}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_change_availability(chargepoint_id, connector_id, availability_type):
    message = requests.post("http://localhost:9000/ocpp16/changeavailability/" + chargepoint_id, json={"connector_id": connector_id, "type": availability_type}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_change_configuration(chargepoint_id, key, value):
    message = requests.post("http://localhost:9000/ocpp16/changeconfiguration/" + chargepoint_id, json={"key": key, "value": value}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_clear_cache(chargepoint_id):
    message = requests.post("http://localhost:9000/ocpp16/clearcache/" + chargepoint_id).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_unlock_connector(chargepoint_id, connector_id):
    message = requests.post("http://localhost:9000/ocpp16/unlockconnector/" + chargepoint_id, json={"connector_id": connector_id}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_get_configuration(chargepoint_id, keys):
    message = requests.post("http://localhost:9000/ocpp16/getconfiguration/" + chargepoint_id, json={"keys": keys}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_get_composite_schedule_task(chargepoint_id, connector_id, duration, charging_rate_unit_type):
    message = requests.post("http://localhost:9000/ocpp16/getcompositeschedule/" + chargepoint_id, json={"connector_id": connector_id, "duration": duration, "charging_rate_unit": charging_rate_unit_type}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_clear_charging_profile_task(chargepoint_id, charging_profile_id, connector_id, charging_profile_purpose_type, stack_level):
    message = requests.post("http://localhost:9000/ocpp16/clearchargingprofile/" + chargepoint_id, json={"charging_profile_id": charging_profile_id,"connector_id": connector_id, "charging_profile_purpose":charging_profile_purpose_type, "stack_level": stack_level}).json()
    send_task_update(message)
    return message


@shared_task()
def ocpp16_set_charging_profile_task(chargepoint_id, connector_id, charging_profile_id):
    message = requests.post("http://localhost:9000/ocpp16/setchargingprofile/" + chargepoint_id, json={"connector_id": connector_id, "charging_profile_id": charging_profile_id}).json()
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