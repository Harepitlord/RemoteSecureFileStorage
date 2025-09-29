"""
Common mixins for role-based access control and general functionality
"""
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages
from UserManagement.models import UserGroups


class RoleRequiredMixin(AccessMixin):
    """
    Mixin that restricts access based on user role.
    """
    required_roles = []  # Override in subclass

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if hasattr(request.user, 'role') and request.user.role not in self.required_roles:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('hub:Home')

        return super().dispatch(request, *args, **kwargs)


class AuthorityRequiredMixin(RoleRequiredMixin):
    """Mixin that requires Authority role"""
    required_roles = [UserGroups.authority]


class LogisticsRequiredMixin(RoleRequiredMixin):
    """Mixin that requires Logistics role"""
    required_roles = [UserGroups.logistics]


class ShipperRequiredMixin(RoleRequiredMixin):
    """Mixin that requires Shipper role"""
    required_roles = [UserGroups.shipper]


class MultiRoleRequiredMixin(RoleRequiredMixin):
    """Mixin that allows multiple roles"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow setting required_roles dynamically
        if not hasattr(self, 'required_roles') or not self.required_roles:
            self.required_roles = ['authority', 'logistics']  # Default fallback


class AdminRequiredMixin(AccessMixin):
    """Mixin that requires admin/staff privileges"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Admin privileges required to access this page.')
            return redirect('hub:Home')
        
        return super().dispatch(request, *args, **kwargs)
