from django.db import models

# Create your models here.
class Transaction(models.Model):
    transaction_id = models.IntegerField()
    start_transaction_timestamp = models.DateTimeField()
    stop_transaction_timestamp = models.DateTimeField()
    wh_meter_start = models.IntegerField()
    wh_meter_stop = models.IntegerField()
    #id_tag = 
    #reservation_id =