"""
Custom mixins for view-level security and availability checks
"""
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from .notifications import check_user_availability, NotificationManager
from common.mixins import RoleRequiredMixin, AuthorityRequiredMixin, LogisticsRequiredMixin, ShipperRequiredMixin


class RSAKeyRequiredMixin(AccessMixin):
    """
    Mixin that ensures user has RSA keys before accessing the view.
    Similar to LoginRequiredMixin but for RSA key requirement.
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.has_rsa_keys():
            # Create notification if not already exists
            existing_notification = request.user.notifications.filter(
                notification_type='KEY_GENERATION_REQUIRED',
                is_read=False
            ).first()
            
            if not existing_notification:
                NotificationManager.notify_key_generation_required(request.user)
            
            messages.warning(
                request, 
                'RSA keys are required to access this feature. Please generate your keys first.'
            )
            return redirect('UserManagement:Profile')
        
        return super().dispatch(request, *args, **kwargs)


class AvailabilityRequiredMixin(AccessMixin):
    """
    Mixin that checks if required user types (Authority/Logistics) are available
    before allowing access to shipment creation features.
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        availability = check_user_availability()
        
        if not availability['authority_available']:
            messages.error(
                request,
                'Cannot create shipment: No Authority users are available for approval. Please contact your administrator.'
            )
            return redirect('hub:ShipperDashboard')
        
        if not availability['logistics_available']:
            messages.error(
                request,
                'Cannot create shipment: No Logistics users are available for handling. Please contact your administrator.'
            )
            return redirect('hub:ShipperDashboard')
        
        return super().dispatch(request, *args, **kwargs)


class ShipmentAccessMixin(AccessMixin):
    """
    Mixin that ensures user has proper access to shipment-related features.
    Combines RSA key requirement with availability checks.
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # First check RSA keys
        if not request.user.has_rsa_keys():
            existing_notification = request.user.notifications.filter(
                notification_type='KEY_GENERATION_REQUIRED',
                is_read=False
            ).first()
            
            if not existing_notification:
                NotificationManager.notify_key_generation_required(request.user)
            
            messages.warning(
                request, 
                'RSA keys are required to access encrypted shipment files. Please generate your keys first.'
            )
            return redirect('UserManagement:Profile')
        
        # Then check availability for shipment creation
        if request.resolver_match.url_name in ['NewShipment', 'makeShipment']:
            availability = check_user_availability()
            
            if not availability['authority_available'] or not availability['logistics_available']:
                missing_types = []
                if not availability['authority_available']:
                    missing_types.append('Authority users')
                if not availability['logistics_available']:
                    missing_types.append('Logistics users')
                
                messages.error(
                    request,
                    f'Cannot create shipment: {" and ".join(missing_types)} are not available. Please contact your administrator.'
                )
                return redirect('hub:ShipperDashboard')
        
        return super().dispatch(request, *args, **kwargs)


# Role-based mixins are now imported from common.mixins
