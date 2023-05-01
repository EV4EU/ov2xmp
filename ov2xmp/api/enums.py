from enum import Enum
from django.db import models


class AvailabilityStatus(models.IntegerChoices):
    ACCEPTED = 1
    REJECTED = 2
    SCHEDULED = 3


class ChargePointStatus(models.IntegerChoices):
    AVAILABLE = 1
    PREPARING = 2
    CHARGING = 3
    SUSPENDED_EVSE = 4
    SUSPENDED_EV = 5
    FINISHING = 6
    RESERVED = 7
    UNAVAILABLE = 8
    FAULTED = 9