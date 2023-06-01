from rest_framework import serializers


class OcppResetSerializer(serializers.Serializer):
    reset_type = serializers.ChoiceField(choices=("soft", "hard"))
    chargepoint_url_identity = serializers.CharField(max_length=255)
    class Meta:
        fields = "__all__"

class OcppRemoteStartTransactionSerializer(serializers.Serializer):
    connector_id = serializers.IntegerField(default=None)
    chargepoint_url_identity = serializers.CharField(max_length=255)
    id_tag = serializers.CharField(max_length=255)
    class Meta:
        fields = "__all__"

class OcppRemoteStopTransactionSerializer(serializers.Serializer):
    transaction_id = serializers.IntegerField()
    chargepoint_url_identity = serializers.CharField(max_length=255)
    class Meta:
        fields = "__all__"
