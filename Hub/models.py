from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.
class Shipment(models.Model):
    class CargoTypes(models.TextChoices):
        INFLAMMABLE = "Inflammable"
        Fragile = "Fragile"
        Hazardous = "Hazardous"
        Live_stock = "Live-stock"
        Perishable = "Perishable"

    shipmentId = models.CharField(name="shipmentId", max_length=20)
    ShipperName = models.CharField(name="Shipper_Name", max_length=40)
    ShipmentCompany = models.CharField(name="Shipment_Company", max_length=40)
    ReceiverName = models.CharField(name="Receiver_Name", max_length=30)
    source = models.CharField(name="Source", max_length=25)
    destination = models.CharField(name="Destination", max_length=25)
    cargoName = models.CharField(name="Cargo_Name", max_length=35)
    cargoType = models.CharField(name="Cargo_Type", max_length=20, choices=CargoTypes.choices)

    manager = models.Manager()


class Documents(models.Model):
    documentName = models.CharField(name="Document_Name", max_length=50)
    document = models.FileField(name="Cargo_Doc")

    shipmentId = models.ForeignKey(to=Shipment, on_delete=models.CASCADE)


class Shipper(models.Model):
    shipperId = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    shipment = models.ForeignKey(to=Shipment, on_delete=models.CASCADE)

    manager = models.Manager()


class ShipmentAccess(models.Model):
    userid = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    shipment = models.ForeignKey(to=Shipment, on_delete=models.CASCADE)
    # access = models.CharField()
