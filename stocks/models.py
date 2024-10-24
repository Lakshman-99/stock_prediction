from django.db import models


class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.FloatField()
    close_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    volume = models.IntegerField()


class StockPrediction(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    predicted_price = models.FloatField()
