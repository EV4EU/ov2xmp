from rest_framework import serializers
from .models import Chargingprofile


class ChargingprofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chargingprofile
        fields = "__all__"
