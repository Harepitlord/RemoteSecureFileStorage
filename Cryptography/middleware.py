"""
Middleware for RSA key validation and user flow management
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .notifications import NotificationManager


class RSAKeyRequiredMiddleware:
    """
    Middleware to ensure users have RSA keys before accessing certain features
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that require RSA keys
        self.protected_urls = [
            '/shipper/makeShipment',
            '/shipper/shipmentHistory',
            '/authority/listApprovals',
            '/logistics/',
        ]
        
        # URLs to exclude from RSA key check
        self.excluded_urls = [
            '/UserManagement/login',
            '/UserManagement/logout',
            '/UserManagement/signup',
            '/UserManagement/profile',
            '/about',
            '/admin/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Skip middleware for excluded URLs
        if any(request.path.startswith(url) for url in self.excluded_urls):
            response = self.get_response(request)
            return response
        
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            response = self.get_response(request)
            return response
        
        # Check if user needs RSA keys for protected URLs
        if any(request.path.startswith(url) for url in self.protected_urls):
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
                    'RSA keys are required to access encrypted files. Please generate your keys first.'
                )
                return redirect('UserManagement:Profile')
        
        response = self.get_response(request)
        return response


class NotificationContextMiddleware:
    """
    Middleware to add notification context to all requests
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Add notification count to context
            request.unread_notification_count = NotificationManager.get_unread_count(request.user)
            request.recent_notifications = NotificationManager.get_recent_notifications(request.user, 5)
        else:
            request.unread_notification_count = 0
            request.recent_notifications = []
        
        response = self.get_response(request)
        return response
