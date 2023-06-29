from django.db import models
from transaction.models import Transaction
from ocpp.v16 import enums as enums_v16
from django.contrib.postgres.fields import ArrayField
import re
from django.core.exceptions import ValidationError
#from django_validated_jsonfield import ValidatedJSONField as JSONField
from django.core.validators import BaseValidator
import jsonschema
import jsonschema.exceptions
from django.core.exceptions import ValidationError


class JSONSchemaValidator(BaseValidator):
    def compare(self, value, schema):
        try:
            jsonschema.validate(value, schema)
            
        except jsonschema.exceptions.ValidationError:
            raise ValidationError(
                '%(value)s failed JSON schema check', params={'value': value}
            )


class ChargingSchedulePeriod:
    def __init__(self, startPeriod, limit, number_phases):
        self.startPeriod = startPeriod
        self.limit = limit
        self.number_phases = number_phases
    
    def to_dict(self):
        return {
            "startPeriod": self.startPeriod,
            "limit": self.limit,
            "number_phases": self.number_phases
        }


class ChargingSchedulePeriodCreator:
  
    def __init__(self, field):
        self.field = field
  
    def __get__(self, obj):
        if obj is None:
            return self
        return obj.__dict__(self.field.name)
  
    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.convert_input(value)

    def convert_input(self, value):
        if value is None:
            return None
        
        if isinstance(value, ChargingSchedulePeriod):
            return value
        else:
            return ChargingSchedulePeriod(**value)


class ChargingSchedulePeriodField(models.JSONField):
    description = "A ChargingSchedule object"
    
    def from_db_value(self, value, expression, connection):
        db_val = super().from_db_value(value, expression, connection)

        if db_val is None:
            return db_val
        
        return ChargingSchedulePeriod(**db_val)
    
    def get_prep_value(self, value):
        dict_value = value.to_dict()
        prep_value = super().get_prep_value(dict_value)
        return prep_value

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only=private_only)
        setattr(cls, self.name, ChargingSchedulePeriodCreator(self))


# Create your models here.
class Chargingprofile(models.Model):

    _data_schema = {
        "type": "object",
        "properties": {
            "startPeriod": {"type": "string", "default": "", "example":"Name", "title":"Name"},
            "limit": {"type": "number", "default": 0,   "example":"Nom", "title":"Nom"},
            "number_phases": {"type": "integer", "default": 1, "example":"Nom", "title":"Nom"},
        },
        #"default": {}, #note the top level default
        "required": ['startPeriod', 'limit', 'number_phases'],
        "additionalProperties": False,
    }

    chargingprofile_id = models.IntegerField(primary_key=True)
    transaction_id = models.ForeignKey(Transaction, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    stack_level = models.IntegerField()
    chargingprofile_purpose = models.CharField(choices=[(i.value, i.value) for i in enums_v16.ChargingProfilePurposeType], default=enums_v16.ChargingProfilePurposeType.charge_point_max_profile.value, max_length=21)
    chargingprofile_kind = models.CharField(choices=[(i.value, i.value) for i in enums_v16.ChargingProfileKindType], default=enums_v16.ChargingProfileKindType.absolute.value, max_length=10)
    recurrency_kind = models.CharField(choices=[(i.value, i.value) for i in enums_v16.RecurrencyKind], default=None, null=True, max_length=10)
    valid_from = models.DateTimeField(default=None, null=True, blank=True)
    valid_to = models.DateTimeField(default=None, null=True, blank=True)
    ## ChargingSchedule attributes
    duration = models.IntegerField(default=None, null=True, blank=True)
    start_schedule = models.DateTimeField(default=None, null=True, blank=True)
    charging_rate_unit = models.CharField(choices=[(i.value, i.value) for i in enums_v16.ChargingRateUnitType], default=enums_v16.ChargingRateUnitType.watts.value, max_length=1)
    chargingschedule_period = ArrayField(models.JSONField(validators=[JSONSchemaValidator(limit_value=_data_schema)]))
    min_charging_rate = models.DecimalField(default=None, null=True, max_digits=5, decimal_places=1, blank=True)
