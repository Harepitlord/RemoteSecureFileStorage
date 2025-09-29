"""
Notification utilities for the RemoteSecureFileStorage system
"""
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Notification
from UserManagement.models import UserGroups

CustomUser = get_user_model()


class NotificationManager:
    """Centralized notification management"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type, shipment=None):
        """Create a new notification for a user"""
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            shipment=shipment
        )
    
    @staticmethod
    def notify_shipment_created(shipment):
        """Notify all authority users when a shipment is created"""
        authority_users = CustomUser.objects.filter(role=UserGroups.authority)
        
        for user in authority_users:
            NotificationManager.create_notification(
                user=user,
                title=f"New Shipment: {shipment.shipmentId}",
                message=f"A new shipment has been created by {shipment.created_by.name} and requires approval.",
                notification_type='SHIPMENT_CREATED',
                shipment=shipment
            )
    
    @staticmethod
    def notify_shipment_approved(shipment, authority_user=None):
        """Notify shipper and assigned logistics when shipment is approved"""
        authority_name = authority_user.email if authority_user else (shipment.approved_by.email if shipment.approved_by else 'Authority')

        # Notify shipper
        NotificationManager.create_notification(
            user=shipment.created_by,
            title=f"Shipment Approved: {shipment.shipmentId}",
            message=f"Your shipment has been approved by {authority_name}. Approval document has been generated.",
            notification_type='SUCCESS',
            shipment=shipment
        )
        
        # Notify assigned logistics users
        for assignment in shipment.hub_assignments.filter(is_active=True):
            NotificationManager.create_notification(
                user=assignment.logistics_user,
                title=f"Shipment Approved: {shipment.shipmentId}",
                message=f"Shipment {shipment.shipmentId} has been approved and is ready for logistics handling.",
                notification_type='SHIPMENT_APPROVED',
                shipment=shipment
            )
    
    @staticmethod
    def notify_shipment_rejected(shipment, authority_user=None, reason=None):
        """Notify shipper and assigned logistics when shipment is rejected"""
        authority_name = authority_user.email if authority_user else (shipment.approved_by.email if shipment.approved_by else 'Authority')
        rejection_reason = reason or shipment.rejection_reason or 'No reason provided'

        # Notify shipper
        NotificationManager.create_notification(
            user=shipment.created_by,
            title=f"Shipment Rejected: {shipment.shipmentId}",
            message=f"Your shipment has been rejected by {authority_name}. Reason: {rejection_reason}. Rejection document has been generated.",
            notification_type='ERROR',
            shipment=shipment
        )
        
        # Notify assigned logistics users
        for assignment in shipment.hub_assignments.filter(is_active=True):
            NotificationManager.create_notification(
                user=assignment.logistics_user,
                title=f"Shipment Rejected: {shipment.shipmentId}",
                message=f"Shipment {shipment.shipmentId} has been rejected and may need attention.",
                notification_type='SHIPMENT_REJECTED',
                shipment=shipment
            )
    
    @staticmethod
    def notify_assignment_updated(assignment):
        """Notify logistics user when they are assigned to a shipment"""
        NotificationManager.create_notification(
            user=assignment.logistics_user,
            title=f"New Assignment: {assignment.shipment.shipmentId}",
            message=f"You have been assigned to handle shipment {assignment.shipment.shipmentId}.",
            notification_type='ASSIGNMENT_UPDATED',
            shipment=assignment.shipment
        )
    
    @staticmethod
    def notify_key_generation_required(user):
        """Notify user that RSA key generation is required"""
        NotificationManager.create_notification(
            user=user,
            title="RSA Key Generation Required",
            message="Please generate your RSA keys to access encrypted shipment files.",
            notification_type='KEY_GENERATION_REQUIRED'
        )
    
    @staticmethod
    def notify_document_ready(shipment):
        """Notify relevant users when approval document is ready"""
        users_to_notify = [shipment.created_by]  # Shipper
        
        # Add assigned logistics users
        for assignment in shipment.hub_assignments.filter(is_active=True):
            users_to_notify.append(assignment.logistics_user)
        
        for user in users_to_notify:
            NotificationManager.create_notification(
                user=user,
                title=f"Approval Document Ready: {shipment.shipmentId}",
                message=f"The approval document for shipment {shipment.shipmentId} is now available.",
                notification_type='DOCUMENT_READY',
                shipment=shipment
            )
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for a user"""
        return Notification.objects.filter(user=user, is_read=False).count()
    
    @staticmethod
    def mark_as_read(notification_ids, user):
        """Mark notifications as read"""
        Notification.objects.filter(
            id__in=notification_ids, 
            user=user
        ).update(is_read=True)
    
    @staticmethod
    def get_recent_notifications(user, limit=10):
        """Get recent notifications for a user"""
        return Notification.objects.filter(user=user).order_by('-created_at')[:limit]


def check_user_availability():
    """Check if authority and logistics users are available"""
    authority_count = CustomUser.objects.filter(
        role=UserGroups.authority,
        is_active=True
    ).count()
    
    logistics_count = CustomUser.objects.filter(
        role=UserGroups.logistics,
        is_active=True
    ).count()
    
    return {
        'authority_available': authority_count > 0,
        'logistics_available': logistics_count > 0,
        'authority_count': authority_count,
        'logistics_count': logistics_count
    }
