from django.db import models


class france_immobilier(models.Model):
    date_transaction = models.DateTimeField(blank=True, null=True)
    id_transaction = models.FloatField(blank=True, null=True)
    ville = models.TextField(blank=True, null=True)
    departement = models.FloatField(blank=True, null=True)
    prix = models.FloatField(blank=True, null=True)
    pps = models.FloatField(blank=True, null=True)
    type_batiment = models.TextField(blank=True, null=True)
    interest = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hist'