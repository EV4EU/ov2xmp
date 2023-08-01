from rest_framework import serializers
from transaction.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    id_tag = serializers.SlugRelatedField(many=False, read_only=True, slug_field="idToken")
    class Meta:
        model = Transaction
        fields = "__all__"
