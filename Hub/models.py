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

    class ShipmentStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted for Approval"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    shipmentId = models.CharField(name="shipmentId", max_length=20, unique=True)
    ShipperName = models.CharField(name="Shipper_Name", max_length=40)
    ShipmentCompany = models.CharField(name="Shipment_Company", max_length=40)
    ReceiverName = models.CharField(name="Receiver_Name", max_length=30)
    source = models.CharField(name="Source", max_length=25)
    destination = models.CharField(name="Destination", max_length=25)
    cargoName = models.CharField(name="Cargo_Name", max_length=35)
    cargoType = models.CharField(name="Cargo_Type", max_length=20, choices=CargoTypes.choices)

    # New fields for enhanced workflow
    status = models.CharField(max_length=20, choices=ShipmentStatus.choices, default=ShipmentStatus.DRAFT)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='created_shipments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Approval fields
    approved_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_shipments')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Versioning
    version = models.IntegerField(default=1)
    parent_shipment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='versions')

    objects = models.Manager()

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

    objects = models.Manager()


class ShipmentAccess(models.Model):
    class AccessLevels(models.TextChoices):
        OWNER = "Owner"
        VIEWER = "Viewer"

    userid = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    shipment = models.ForeignKey(to=Shipment, on_delete=models.CASCADE)
    access = models.CharField(max_length=20, choices=AccessLevels.choices, default=AccessLevels.OWNER)


class ShipmentAssignment(models.Model):
    """Track logistics assignments to shipments"""

    class AssignmentStatus(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        DELIVERED = "DELIVERED", "Delivered"
        FAILED = "FAILED", "Delivery Failed"

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='hub_assignments')
    logistics_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='hub_assigned_shipments',
        limit_choices_to={'role': 'logistics'}
    )
    assigned_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='hub_assignments_made'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.ASSIGNED)
    pickup_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    objects = models.Manager()

    class Meta:
        unique_together = ['shipment', 'logistics_user']

    def __str__(self):
        return f"{self.shipment.shipmentId} -> {self.logistics_user.email}"

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

    objects = models.Manager()

