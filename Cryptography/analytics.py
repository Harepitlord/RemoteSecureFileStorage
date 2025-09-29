"""
Analytics and dashboard utilities for shipment data
"""
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from UserManagement.models import UserGroups

CustomUser = get_user_model()


class ShipmentAnalytics:
    """Analytics for shipment data and user activities"""
    
    @staticmethod
    def get_shipment_status_distribution():
        """Get distribution of shipments by status"""
        from Hub.models import Shipment
        return Shipment.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
    
    @staticmethod
    def get_shipment_trends(days=30):
        """Get shipment creation trends over specified days"""
        from Hub.models import Shipment
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Group by date
        trends = []
        current_date = start_date.date()

        while current_date <= end_date.date():
            count = Shipment.objects.filter(
                created_at__date=current_date
            ).count()

            trends.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            current_date += timedelta(days=1)

        return trends
    
    @staticmethod
    def get_cargo_type_distribution():
        """Get distribution of shipments by cargo type"""
        from Hub.models import Shipment
        return Shipment.objects.values('Cargo_Type').annotate(
            count=Count('id')
        ).order_by('-count')
    
    @staticmethod
    def get_user_activity_stats(user):
        """Get activity statistics for a specific user"""
        if user.role == UserGroups.shipper:
            return ShipmentAnalytics._get_shipper_stats(user)
        elif user.role == UserGroups.authority:
            return ShipmentAnalytics._get_authority_stats(user)
        elif user.role == UserGroups.logistics:
            return ShipmentAnalytics._get_logistics_stats(user)
        else:
            return {}
    
    @staticmethod
    def _get_shipper_stats(user):
        """Get statistics for shipper user"""
        from Hub.models import Shipment
        total_shipments = Shipment.objects.filter(created_by=user).count()
        pending_shipments = Shipment.objects.filter(
            created_by=user,
            status=Shipment.ShipmentStatus.SUBMITTED
        ).count()
        approved_shipments = Shipment.objects.filter(
            created_by=user,
            status=Shipment.ShipmentStatus.APPROVED
        ).count()
        rejected_shipments = Shipment.objects.filter(
            created_by=user,
            status=Shipment.ShipmentStatus.REJECTED
        ).count()
        
        return {
            'total_shipments': total_shipments,
            'pending_shipments': pending_shipments,
            'approved_shipments': approved_shipments,
            'rejected_shipments': rejected_shipments,
            'approval_rate': (approved_shipments / total_shipments * 100) if total_shipments > 0 else 0
        }
    
    @staticmethod
    def _get_authority_stats(user):
        """Get statistics for authority user"""
        from Hub.models import Shipment
        total_reviewed = Shipment.objects.filter(approved_by=user).count()
        approved_count = Shipment.objects.filter(
            approved_by=user,
            status=Shipment.ShipmentStatus.APPROVED
        ).count()
        rejected_count = Shipment.objects.filter(
            approved_by=user,
            status=Shipment.ShipmentStatus.REJECTED
        ).count()
        pending_review = Shipment.objects.filter(
            status=Shipment.ShipmentStatus.SUBMITTED
        ).count()
        
        return {
            'total_reviewed': total_reviewed,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'pending_review': pending_review,
            'approval_rate': (approved_count / total_reviewed * 100) if total_reviewed > 0 else 0
        }
    
    @staticmethod
    def _get_logistics_stats(user):
        """Get statistics for logistics user"""
        from Cryptography.models import ShipmentAssignment
        
        assigned_shipments = ShipmentAssignment.objects.filter(
            logistics_user=user,
            is_active=True
        ).count()
        
        from Hub.models import Shipment
        completed_assignments = ShipmentAssignment.objects.filter(
            logistics_user=user,
            shipment__status=Shipment.ShipmentStatus.APPROVED
        ).count()
        
        return {
            'assigned_shipments': assigned_shipments,
            'completed_assignments': completed_assignments,
            'active_assignments': assigned_shipments
        }
    
    @staticmethod
    def get_recent_ledger_entries(user, limit=10):
        """Get recent ledger entries relevant to the user"""
        from Hub.models import Ledger
        if user.role == UserGroups.shipper:
            # Show entries for shipments created by this user
            return Ledger.objects.filter(
                shipmentId__created_by=user
            ).select_related('userId', 'shipmentId').order_by('-id')[:limit]

        elif user.role == UserGroups.authority:
            # Show all entries for review and approval activities
            return Ledger.objects.all().select_related(
                'userId', 'shipmentId'
            ).order_by('-id')[:limit]

        elif user.role == UserGroups.logistics:
            # Show entries for assigned shipments
            from Cryptography.models import ShipmentAssignment
            assigned_shipment_ids = ShipmentAssignment.objects.filter(
                logistics_user=user,
                is_active=True
            ).values_list('shipment_id', flat=True)

            return Ledger.objects.filter(
                shipmentId__id__in=assigned_shipment_ids
            ).select_related('userId', 'shipmentId').order_by('-id')[:limit]

        return Ledger.objects.none()
    
    @staticmethod
    def get_monthly_shipment_summary():
        """Get monthly summary of shipments"""
        from Hub.models import Shipment
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)

        current_month_count = Shipment.objects.filter(
            created_at__gte=current_month_start
        ).count()

        last_month_count = Shipment.objects.filter(
            created_at__gte=last_month_start,
            created_at__lt=current_month_start
        ).count()
        
        return {
            'current_month': current_month_count,
            'last_month': last_month_count,
            'growth': ((current_month_count - last_month_count) / last_month_count * 100) if last_month_count > 0 else 0
        }


class LedgerManager:
    """Enhanced ledger management with detailed tracking"""
    
    EVENT_DESCRIPTIONS = {
        'CREATE': 'Shipment created and submitted for approval',
        'APPROVED': 'Shipment approved by authority',
        'SHARED': 'Shipment shared with user',
        'ACCESS_REQUEST': 'Access requested for shipment',
        'APPROVE_ACCESS': 'Access approved for shipment',
        'APPROVE_REQUEST': 'Approval requested for shipment',
        'REJECTED': 'Shipment rejected by authority',
        'DOCUMENT_GENERATED': 'Approval document generated',
        'LOGISTICS_ASSIGNED': 'Logistics user assigned to shipment',
        'FILE_ACCESSED': 'Shipment file accessed',
        'NOTIFICATION_SENT': 'Notification sent to user',
    }
    
    @staticmethod
    def log_event(user, shipment, event, details=None):
        """Log an event to the ledger with enhanced details"""
        from Hub.models import Ledger
        # Create the basic ledger entry
        ledger_entry = Ledger.objects.create(
            userId=user,
            shipmentId=shipment,
            event=event
        )
        
        # Create notification based on event type
        from .notifications import NotificationManager
        
        if event == 'APPROVED':
            NotificationManager.notify_shipment_approved(shipment)
        elif event == 'REJECTED':
            NotificationManager.notify_shipment_rejected(shipment)
        elif event == 'LOGISTICS_ASSIGNED':
            # Find the assignment and notify
            from .models import ShipmentAssignment
            assignment = ShipmentAssignment.objects.filter(
                shipment=shipment,
                is_active=True
            ).first()
            if assignment:
                NotificationManager.notify_assignment_updated(assignment)
        
        return ledger_entry
    
    @staticmethod
    def get_shipment_timeline(shipment):
        """Get complete timeline for a shipment"""
        from Hub.models import Ledger
        entries = Ledger.objects.filter(
            shipmentId=shipment
        ).select_related('userId').order_by('id')
        
        timeline = []
        for entry in entries:
            timeline.append({
                'event': entry.event,
                'description': LedgerManager.EVENT_DESCRIPTIONS.get(entry.event, entry.event),
                'user': entry.userId,
                'timestamp': entry.id,  # Using ID as timestamp since no created_at field
                'shipment': entry.shipmentId
            })
        
        return timeline
    
    @staticmethod
    def get_user_activity_feed(user, limit=20):
        """Get activity feed for a user with rich context"""
        entries = ShipmentAnalytics.get_recent_ledger_entries(user, limit)
        
        feed = []
        for entry in entries:
            feed.append({
                'event': entry.event,
                'description': LedgerManager.EVENT_DESCRIPTIONS.get(entry.event, entry.event),
                'user': entry.userId,
                'shipment': entry.shipmentId,
                'timestamp': entry.id,
                'is_own_action': entry.userId == user
            })
        
        return feed
