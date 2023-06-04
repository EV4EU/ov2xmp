from rest_framework import serializers
from ocpp.v16 import enums as ocppv16_enums


class OcppCommandSerializer(serializers.Serializer):
    chargepoint_id = serializers.CharField(max_length=255)
    sync = serializers.BooleanField(required=False, default=False)
    class Meta:
        fields = "__all__"


class OcppResetSerializer(OcppCommandSerializer):
    reset_type = serializers.ChoiceField(choices=tuple(member.value for member in ocppv16_enums.ResetType))


class OcppRemoteStartTransactionSerializer(OcppCommandSerializer):
    connector_id = serializers.IntegerField(default=None)
    id_tag = serializers.CharField(max_length=255)


class OcppRemoteStopTransactionSerializer(OcppCommandSerializer):
    transaction_id = serializers.IntegerField()


class OcppReserveNowSerializer(OcppCommandSerializer):
    connector_id = serializers.IntegerField(required=False, default=None)
    id_tag = serializers.CharField(max_length=255)
    expiry_date = serializers.DateTimeField()
    reservation_id = serializers.IntegerField(required=False, default=None)


class OcppCancelReservationSerializer(OcppCommandSerializer):
    reservation_id = serializers.IntegerField()


class OcppChangeAvailabilitySerializer(OcppCommandSerializer):
    connector_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=tuple(member.value for member in ocppv16_enums.AvailabilityType))


class OcppGetConfigurationSerializer(OcppCommandSerializer):
    keys = serializers.ListField(child=serializers.CharField(max_length=50), required=False, default=None)
