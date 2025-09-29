from django.db import models
from django.contrib.auth import get_user_model
from Hub.models import Shipment

CustomUser = get_user_model()


class Notification(models.Model):
    """Notification system for all users"""
    NOTIFICATION_TYPES = [
        ('SHIPMENT_CREATED', 'Shipment Created'),
        ('SHIPMENT_APPROVED', 'Shipment Approved'),
        ('SHIPMENT_REJECTED', 'Shipment Rejected'),
        ('ASSIGNMENT_UPDATED', 'Assignment Updated'),
        ('KEY_GENERATION_REQUIRED', 'RSA Key Generation Required'),
        ('DOCUMENT_READY', 'Approval Document Ready'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


# ShipmentAssignment model moved to Hub app


class FileEncryptionKey(models.Model):
    """Store encrypted AES keys for multi-user file access"""
    KEY_TYPES = [
        ('OWNER', 'Shipment Owner'),
        ('ASSIGNED', 'Assigned Logistics'),
        ('AUTHORITY', 'Authority User'),
    ]
    
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='encryption_keys')
    encrypted_aes_key = models.BinaryField()  # AES key encrypted with user's RSA public key
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='file_keys')
    key_type = models.CharField(max_length=20, choices=KEY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    file_hash = models.CharField(max_length=64, blank=True)  # SHA-256 hash for integrity
    
    class Meta:
        unique_together = ['shipment', 'user', 'key_type']
    
    def __str__(self):
        return f"{self.shipment.shipmentId} - {self.user.email} ({self.key_type})"


class ApprovalDocument(models.Model):
    """Generated approval documents"""

    class DocumentTypes(models.TextChoices):
        APPROVAL = "APPROVAL", "Approval Certificate"
        REJECTION = "REJECTION", "Rejection Certificate"

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='approval_documents')
    document_type = models.CharField(max_length=20, choices=DocumentTypes.choices, default=DocumentTypes.APPROVAL)
    document_path = models.CharField(max_length=500, blank=True)  # Path to encrypted PDF (optional)
    file_data = models.BinaryField()  # Store PDF data directly
    generated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    document_hash = models.CharField(max_length=64, blank=True)  # SHA-256 hash
    
    def __str__(self):
        return f"Approval Doc - {self.shipment.shipmentId}"
