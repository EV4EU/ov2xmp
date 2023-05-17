from django.db import models
from users.models import User


# Create your models here.
class IdTag(models.Model):
    idToken = models.CharField(max_length=255, primary_key=True)
    expiry_date = models.DateTimeField(blank=True, default=None, null=True)
    revoked = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)