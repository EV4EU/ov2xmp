from django.shortcuts import render
from django.http import JsonResponse
import dashboard.management.commands.central_system_v16 as csms 

# Create your views here.
async def soft_reset(request, chargepoint_id):
    if csms.soft_reset(chargepoint_id):
        return JsonResponse({"status": "success", "message": "Soft Reset succcessful"})
    else:
        return JsonResponse({"status": "error", "message": "Failed to send Soft Reset"})
