from rest_framework import serializers
from .models import Location
from django_countries.serializers import CountryFieldMixin


class LocationSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"
