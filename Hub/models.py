from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.urls import reverse


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

    def get_absolute_url(self):
        return reverse('hub:ShipperDetail', args=[str(self.pk)])

    def get_approve_url(self):
        return reverse('hub:AuthorityRequest',args=[str(self.pk)])


def getFileUploadPath(instance , filename):
    return f"{instance.shipmentId.shipmentId}/{filename}"


class Documents(models.Model):
    document = models.FileField(name="Cargo_Doc", upload_to=getFileUploadPath)

    shipmentId = models.ForeignKey(to=Shipment, on_delete=models.CASCADE)


class Shipper(models.Model):
    shipperId = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    shipment = models.ForeignKey(to=Shipment, on_delete=models.CASCADE)

    manager = models.Manager()


class ShipmentAccess(models.Model):
    class AccessLevels(models.TextChoices):
        OWNER = "Owner"
        VIEWER = "Viewer"

    userid = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    shipment = models.ForeignKey(to=Shipment, on_delete=models.CASCADE)
    access = models.CharField(max_length=20, choices=AccessLevels.choices, default=AccessLevels.OWNER)


class ShipmentAccessRequests(models.Model):
    requester = models.ForeignKey(to=get_user_model(), related_name='Requester', on_delete=models.CASCADE)
    shipmentId = models.ForeignKey(to=get_user_model(), related_name='ShipmentId', on_delete=models.CASCADE)


class Ledger(models.Model):
    class Events(models.TextChoices):
        CREATE = "CREATE"
        APPROVED = "APPROVED"
        SHARED = "SHARED"
        ACCESS_REQUEST = "ACCESS_REQUEST"
        APPROVE_ACCESS = "APPROVE_ACCESS"
        APPROVE_REQUEST = "APPROVE_REQUEST"

    userId = models.ForeignKey(to=get_user_model(),related_name='LedgerUser',on_delete=models.CASCADE)
    shipmentId = models.ForeignKey(to=Shipment,related_name='LedgerShipment',on_delete=models.CASCADE)
    event = models.CharField(max_length=20,choices=Events.choices)

    manager = models.Manager()

