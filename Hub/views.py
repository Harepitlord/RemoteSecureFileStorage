import string
import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone

from Hub import models, forms
from Cryptography.notifications import NotificationManager, check_user_availability
from Cryptography.mixins import ShipmentAccessMixin
from common.mixins import AuthorityRequiredMixin, LogisticsRequiredMixin
from Cryptography.file_encryption import ShipmentFileManager
from Cryptography.analytics import ShipmentAnalytics, LedgerManager
from Cryptography.document_generator import generate_approval_pdf


def generate_unique_alphanumeric(length):
    alphanumeric = string.ascii_letters + string.digits
    while True:
        generated_text = ''.join(random.choice(alphanumeric) for _ in range(length))
        if generated_text not in models.Shipment.manager.all().filter(shipmentId=generated_text):
            return generated_text


# Create your views here.
class Home(View):
    def get(self, request):
        return redirect(to=reverse_lazy('UserManagement:Login'))
        # return render(request=request, template_name="hub/home.html")


class DashBoard(LoginRequiredMixin, View):

    def get(self, request):
        # Get notifications for the user
        from Cryptography.models import Notification
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')

        context = {
            'notifications': notifications,
        }
        return render(request=request, template_name="hub/enhanced_dashboard.html", context=context)


class About(View):
    def get(self, request: HttpRequest):
        context = {}
        if request.user.is_authenticated:
            context['base'] = 'Hub/LoginBase.html'
        else:
            context['base'] = 'Hub/NonLoginBase.html'
        return render(request=request, template_name='hub/About.html', context=context)


class ShipperDashboard(LoginRequiredMixin, View):

    def get(self, request: HttpRequest):
        # Get user statistics
        user_stats = ShipmentAnalytics.get_user_activity_stats(request.user)

        # Get recent shipments
        recent_shipments = models.Shipment.objects.filter(
            created_by=request.user
        ).order_by('-created_at')[:5]

        # Get activity feed
        activity_feed = LedgerManager.get_user_activity_feed(request.user, 10)

        # Get shipment status distribution for user
        status_distribution = models.Shipment.objects.filter(
            created_by=request.user
        ).values('status').annotate(count=Count('id'))

        # Get all notifications for the modal
        from Cryptography.models import Notification
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')

        context = {
            'user_stats': user_stats,
            'recent_shipments': recent_shipments,
            'activity_feed': activity_feed,
            'status_distribution': list(status_distribution),
            'notifications': notifications,
        }
        return render(request=request, template_name='hub/enhanced_shipper_dashboard.html', context=context)


class ShipperListShipments(LoginRequiredMixin, ListView):
    model = models.Shipper
    context_object_name = 'shipmentList'
    paginate_by = 25
    template_name = "hub/ShipperListShipment.html"

    def get_queryset(self):
        return self.model.manager.all().filter(self.request.user.pk)


class LogisticsDashboard(LogisticsRequiredMixin, View):

    def get(self, request: HttpRequest):
        # Get user statistics
        user_stats = ShipmentAnalytics.get_user_activity_stats(request.user)

        # Get assigned shipments
        from Cryptography.models import ShipmentAssignment
        assigned_shipments = ShipmentAssignment.objects.filter(
            logistics_user=request.user,
            is_active=True
        ).select_related('shipment')[:5]

        # Get activity feed
        activity_feed = LedgerManager.get_user_activity_feed(request.user, 10)

        # Get shipment status distribution for assigned shipments
        assigned_shipment_ids = ShipmentAssignment.objects.filter(
            logistics_user=request.user,
            is_active=True
        ).values_list('shipment_id', flat=True)

        status_distribution = models.Shipment.objects.filter(
            id__in=assigned_shipment_ids
        ).values('status').annotate(count=Count('id'))

        context = {
            'user_stats': user_stats,
            'assigned_shipments': assigned_shipments,
            'activity_feed': activity_feed,
            'status_distribution': list(status_distribution),
        }
        return render(request=request, template_name='hub/enhanced_logistics_dashboard.html', context=context)


class LogisticsAssignedShipments(LogisticsRequiredMixin, ListView):
    """List view for shipments assigned to the current logistics user"""
    model = models.ShipmentAssignment
    template_name = 'hub/logistics_assigned_shipments.html'
    context_object_name = 'assignments'
    paginate_by = 20

    def get_queryset(self):
        return models.ShipmentAssignment.objects.filter(
            logistics_user=self.request.user,
            is_active=True
        ).select_related('shipment', 'assigned_by').order_by('-assigned_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get statistics
        assignments = models.ShipmentAssignment.objects.filter(logistics_user=self.request.user, is_active=True)
        context['stats'] = {
            'total_assigned': assignments.count(),
            'in_transit': assignments.filter(status=models.ShipmentAssignment.AssignmentStatus.IN_TRANSIT).count(),
            'delivered': assignments.filter(status=models.ShipmentAssignment.AssignmentStatus.DELIVERED).count(),
            'pending_pickup': assignments.filter(status=models.ShipmentAssignment.AssignmentStatus.ASSIGNED).count(),
        }

        return context


class LogisticsShipmentDetail(LogisticsRequiredMixin, DetailView):
    """Detail view for a specific shipment assigned to logistics user"""
    model = models.Shipment
    template_name = 'hub/logistics_shipment_detail.html'
    context_object_name = 'shipment'

    def get_object(self):
        shipment = super().get_object()
        # Ensure the shipment is assigned to the current logistics user
        assignment = models.ShipmentAssignment.objects.filter(
            shipment=shipment,
            logistics_user=self.request.user,
            is_active=True
        ).first()

        if not assignment:
            messages.error(self.request, 'You do not have access to this shipment.')
            return redirect('hub:LogisticsAssignedShipments')

        return shipment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get assignment details
        context['assignment'] = models.ShipmentAssignment.objects.filter(
            shipment=self.object,
            logistics_user=self.request.user,
            is_active=True
        ).first()

        # Get shipment history
        context['history'] = models.Ledger.objects.filter(
            shipment=self.object
        ).order_by('-timestamp')[:10]

        return context


class LogisticsUpdateStatus(LogisticsRequiredMixin, View):
    """Update shipment delivery status"""

    def post(self, request, shipment_id):
        try:
            shipment = models.Shipment.objects.get(id=shipment_id)
            assignment = models.ShipmentAssignment.objects.filter(
                shipment=shipment,
                logistics_user=request.user,
                is_active=True
            ).first()

            if not assignment:
                messages.error(request, 'You do not have access to this shipment.')
                return redirect('hub:LogisticsAssignedShipments')

            new_status = request.POST.get('status')
            notes = request.POST.get('notes', '')

            if new_status in [choice[0] for choice in models.ShipmentAssignment.AssignmentStatus.choices]:
                assignment.status = new_status
                assignment.notes = notes

                from django.utils import timezone
                if new_status == models.ShipmentAssignment.AssignmentStatus.IN_TRANSIT and not assignment.pickup_date:
                    assignment.pickup_date = timezone.now()
                elif new_status == models.ShipmentAssignment.AssignmentStatus.DELIVERED and not assignment.delivery_date:
                    assignment.delivery_date = timezone.now()

                assignment.save()

                # Log the status update
                LedgerManager.log_event(
                    request.user,
                    shipment,
                    f'STATUS_UPDATE_{new_status}',
                    f'Logistics status updated to {new_status}'
                )

                messages.success(request, f'Shipment status updated to {assignment.get_status_display()}.')
            else:
                messages.error(request, 'Invalid status provided.')

            return redirect('hub:LogisticsShipmentDetail', pk=shipment_id)

        except models.Shipment.DoesNotExist:
            messages.error(request, 'Shipment not found.')
            return redirect('hub:LogisticsAssignedShipments')
        except Exception as e:
            messages.error(request, f'Error updating status: {str(e)}')
            return redirect('hub:LogisticsAssignedShipments')


class LogisticsDeliveryTracking(LogisticsRequiredMixin, View):
    """Delivery tracking overview for logistics users"""

    def get(self, request):
        # Get all assignments for the logistics user
        assignments = models.ShipmentAssignment.objects.filter(
            logistics_user=request.user,
            is_active=True
        ).select_related('shipment').order_by('-assigned_at')

        # Group by status
        status_groups = {}
        for status_choice in models.ShipmentAssignment.AssignmentStatus.choices:
            status_code = status_choice[0]
            status_groups[status_code] = assignments.filter(status=status_code)

        # Get recent activity
        recent_activity = LedgerManager.get_user_activity_feed(request.user, limit=10)

        context = {
            'assignments': assignments,
            'status_groups': status_groups,
            'recent_activity': recent_activity,
            'total_assignments': assignments.count(),
        }

        return render(request, 'hub/logistics_delivery_tracking.html', context)


class LogisticsReports(LogisticsRequiredMixin, View):
    """Reports and analytics for logistics users"""

    def get(self, request):
        # Get user's assignment statistics
        assignments = models.ShipmentAssignment.objects.filter(logistics_user=request.user)

        # Calculate performance metrics
        total_assignments = assignments.count()
        delivered_count = assignments.filter(status=models.ShipmentAssignment.AssignmentStatus.DELIVERED).count()
        failed_count = assignments.filter(status=models.ShipmentAssignment.AssignmentStatus.FAILED).count()

        delivery_rate = (delivered_count / total_assignments * 100) if total_assignments > 0 else 0

        # Get monthly statistics
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        thirty_days_ago = timezone.now() - timedelta(days=30)
        monthly_assignments = assignments.filter(assigned_at__gte=thirty_days_ago)

        # Get delivery time statistics
        delivered_assignments = assignments.filter(
            status=models.ShipmentAssignment.AssignmentStatus.DELIVERED,
            pickup_date__isnull=False,
            delivery_date__isnull=False
        )

        avg_delivery_time = None
        if delivered_assignments.exists():
            total_time = sum([
                (assignment.delivery_date - assignment.pickup_date).total_seconds() / 3600  # hours
                for assignment in delivered_assignments
            ])
            avg_delivery_time = total_time / delivered_assignments.count()

        context = {
            'total_assignments': total_assignments,
            'delivered_count': delivered_count,
            'failed_count': failed_count,
            'delivery_rate': round(delivery_rate, 2),
            'monthly_assignments': monthly_assignments.count(),
            'avg_delivery_time': round(avg_delivery_time, 2) if avg_delivery_time else None,
            'recent_assignments': assignments.order_by('-assigned_at')[:10],
        }

        return render(request, 'hub/logistics_reports.html', context)


class NewShipment(ShipmentAccessMixin, CreateView):
    model = models.Shipment
    form_class = forms.ShipmentForm
    template_name = "hub/NewShipment.html"
    success_url = reverse_lazy('hub:ShipmentHistory')

    def form_valid(self, form):
        try:
            # Create shipment with enhanced fields
            shipment = form.save(commit=False)
            shipment.shipmentId = generate_unique_alphanumeric(15)
            shipment.created_by = self.request.user
            shipment.status = models.Shipment.ShipmentStatus.SUBMITTED
            shipment.save()

            # Create related records
            models.Shipper(shipperId=self.request.user, shipment=shipment).save()

            # Handle file upload with encryption
            if 'document' in self.request.FILES:
                uploaded_file = self.request.FILES['document']

                # Encrypt file and create access keys
                encryption_result = ShipmentFileManager.encrypt_and_store_file(
                    uploaded_file, shipment, self.request.user
                )

                # Create document record with encrypted path
                models.Documents.objects.create(
                    Cargo_Doc=uploaded_file.name,  # Store original filename
                    shipmentId=shipment
                )

                messages.info(
                    self.request,
                    f'File encrypted successfully. Access keys created for {encryption_result["created_keys"]} users.'
                )

            models.ShipmentAccess(userid=self.request.user, shipment=shipment,
                                  access=models.ShipmentAccess.AccessLevels.OWNER).save()
            models.Ledger(userId=self.request.user, shipmentId=shipment,
                          event=models.Ledger.Events.CREATE).save()

            # Send notifications to authority users
            NotificationManager.notify_shipment_created(shipment)

            messages.success(self.request, f'Shipment {shipment.shipmentId} created successfully and submitted for approval.')
            return redirect(to=self.success_url)

        except Exception as e:
            messages.error(self.request, f'Failed to create shipment: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ShipmentHistory(ListView):
    model = models.Shipment
    template_name = "hub/ShipperListShipment.html"


class ShipmentReports(ListView):
    model = models.Shipment
    template_name = "hub/ShipperReports.html"


class ShipmentDetailView(DetailView):
    model = models.Shipment
    template_name = "hub/ShipperDetail.html"
    slug_field = "pk"
    slug_url_kwarg = "pk"
    context_object_name = "shipment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shipment = self.get_object()
        form = forms.ShipmentForm(instance=shipment)
        context['form'] = form
        return context


class AuthorityDashboard(AuthorityRequiredMixin, View):

    def get(self, request: HttpRequest):
        # Get user statistics
        user_stats = ShipmentAnalytics.get_user_activity_stats(request.user)

        # Get pending shipments for approval
        pending_shipments = models.Shipment.objects.filter(
            status=models.Shipment.ShipmentStatus.SUBMITTED
        ).order_by('-created_at')[:5]

        # Get recent approved/rejected shipments
        recent_decisions = models.Shipment.objects.filter(
            status__in=[models.Shipment.ShipmentStatus.APPROVED, models.Shipment.ShipmentStatus.REJECTED],
            approved_by=request.user
        ).order_by('-approved_at')[:5]

        # Get overall system analytics
        status_distribution = ShipmentAnalytics.get_shipment_status_distribution()
        cargo_distribution = ShipmentAnalytics.get_cargo_type_distribution()
        monthly_summary = ShipmentAnalytics.get_monthly_shipment_summary()
        shipment_trends = ShipmentAnalytics.get_shipment_trends(30)

        # Get activity feed
        activity_feed = LedgerManager.get_user_activity_feed(request.user, 15)

        context = {
            'user_stats': user_stats,
            'pending_shipments': pending_shipments,
            'recent_decisions': recent_decisions,
            'status_distribution': list(status_distribution),
            'cargo_distribution': list(cargo_distribution),
            'monthly_summary': monthly_summary,
            'shipment_trends': shipment_trends,
            'activity_feed': activity_feed,
        }
        return render(request=request, template_name='hub/enhanced_authority_dashboard.html', context=context)


class ShipmentApprovalView(AuthorityRequiredMixin, View):
    """Handle shipment approval/rejection by authority users"""

    def post(self, request, shipment_id):
        try:
            shipment = models.Shipment.objects.get(id=shipment_id)
            action = request.POST.get('action')

            if action == 'approve':
                shipment.status = models.Shipment.ShipmentStatus.APPROVED
                shipment.approved_by = request.user
                shipment.approved_at = timezone.now()
                shipment.save()

                # Log the approval
                LedgerManager.log_event(request.user, shipment, 'APPROVED')

                # Generate and store approval document
                from Cryptography.models import ApprovalDocument
                pdf_data = generate_approval_pdf(shipment, 'APPROVED', request.user)

                # Save the approval document
                approval_doc = ApprovalDocument.objects.create(
                    shipment=shipment,
                    document_type='APPROVAL',
                    generated_by=request.user,
                    file_data=pdf_data.content
                )

                # Send notifications
                NotificationManager.notify_shipment_approved(shipment, request.user)

                messages.success(request, f'Shipment {shipment.shipmentId} has been approved and approval document generated.')

            elif action == 'reject':
                rejection_reason = request.POST.get('rejection_reason', '')
                if not rejection_reason:
                    messages.error(request, 'Rejection reason is required.')
                    return redirect('hub:AuthorityDashboard')

                shipment.status = models.Shipment.ShipmentStatus.REJECTED
                shipment.approved_by = request.user
                shipment.approved_at = timezone.now()
                shipment.rejection_reason = rejection_reason
                shipment.save()

                # Log the rejection
                LedgerManager.log_event(request.user, shipment, 'REJECTED')

                # Generate and store rejection document
                from Cryptography.models import ApprovalDocument
                pdf_data = generate_approval_pdf(shipment, 'REJECTED', request.user, rejection_reason)

                # Save the rejection document
                approval_doc = ApprovalDocument.objects.create(
                    shipment=shipment,
                    document_type='REJECTION',
                    generated_by=request.user,
                    file_data=pdf_data.content
                )

                # Send notifications
                NotificationManager.notify_shipment_rejected(shipment, request.user, rejection_reason)

                messages.success(request, f'Shipment {shipment.shipmentId} has been rejected and rejection document generated.')

            return redirect('hub:AuthorityDashboard')

        except models.Shipment.DoesNotExist:
            messages.error(request, 'Shipment not found.')
            return redirect('hub:AuthorityDashboard')
        except Exception as e:
            messages.error(request, f'Error processing shipment: {str(e)}')
            return redirect('hub:AuthorityDashboard')


class DownloadApprovalDocumentView(LoginRequiredMixin, View):
    """Download approval/rejection documents"""

    def get(self, request, document_id):
        try:
            from Cryptography.models import ApprovalDocument
            document = get_object_or_404(ApprovalDocument, id=document_id)

            # Check permissions - user must be involved in the shipment
            shipment = document.shipment
            if not (request.user == shipment.created_by or
                   request.user == document.generated_by or
                   request.user.groups.filter(name__in=['Authority', 'Logistics']).exists()):
                messages.error(request, 'You do not have permission to access this document.')
                return redirect('hub:Home')

            # Create response with PDF data
            response = HttpResponse(document.file_data, content_type='application/pdf')
            filename = f"shipment_{shipment.shipmentId}_{document.document_type.lower()}_certificate.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            messages.error(request, f'Error downloading document: {str(e)}')
            return redirect('hub:Home')


class AuthorityApproval(ListView):
    model = models.Shipment
    template_name = "hub/AuthorityApproveRequests.html"
    context_object_name = 'request'

    # def get_queryset(self):
    #     qs = models.Ledger.manager.all().filter(userId=self.request.user)
    #     return qs.filter(event=models.Ledger.Events.APPROVE_REQUEST)


class AuthorityRequestApproval(DetailView):
    model = models.Shipment
    context_object_name = 'request'
    template_name = 'hub/AuthorityRequestApporval.html'
    slug_field = "shipmentId"
    slug_url_kwarg = "ShipmentId"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shipment = self.get_object()
        form = forms.ShipmentApprove(instance=shipment)
        context['form'] = form
        context['shipmentId'] = shipment.shipmentId
        return context


class AuthorityApproveRequest(View):
    def post(self,request: HttpRequest):
        shipmentId = request.POST['shipmentId']
        # models.Ledger(userId=self.request.user,shipmentId=shipmentId,event=models.Ledger.Events.APPROVED).save()
        return redirect(to=reverse_lazy('hub:AuthorityDashboard'))


class NotificationAPIView(LoginRequiredMixin, View):
    """API view to get all notifications for the current user"""

    def get(self, request):
        from Cryptography.models import Notification
        from django.http import JsonResponse

        # Get all notifications for the current user
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')

        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
            })

        return JsonResponse({
            'notifications': notifications_data,
            'unread_count': notifications.filter(is_read=False).count()
        })


class MarkNotificationReadView(LoginRequiredMixin, View):
    """API view to mark a specific notification as read"""

    def post(self, request, notification_id):
        from Cryptography.models import Notification
        from django.http import JsonResponse

        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )
            notification.is_read = True
            notification.save()

            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    """API view to mark all notifications as read for the current user"""

    def post(self, request):
        from Cryptography.models import Notification
        from django.http import JsonResponse

        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })


class NotificationUnreadCountView(LoginRequiredMixin, View):
    """API view to get unread notification count"""

    def get(self, request):
        from Cryptography.models import Notification
        from django.http import JsonResponse

        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return JsonResponse({'count': unread_count})

