from django.shortcuts import render
from django.http import JsonResponse
import dashboard.management.commands.central_system_v16 as csms 
import requests
import json

# Create your views here.
def soft_reset(request, chargepoint_id):
    x = requests.get("localhost:5688/ocpp/reset/soft/" + chargepoint_id).json()
    if x["status"] == "success":
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"status": "fail"})
