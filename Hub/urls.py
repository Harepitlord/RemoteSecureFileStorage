from django.urls import path

from Hub import views

app_name='hub'
urlpatterns = [
    path('',views.Home.as_view(),name='Home'),
    path('home',views.DashBoard.as_view(),name='Dashboard'),
    path('about',views.About.as_view(),name='About'),

    path('logistics/home',views.LogisticsDashboard.as_view(),name='LogisticsDashboard'),
    path('logistics/assigned',views.LogisticsAssignedShipments.as_view(),name='LogisticsAssignedShipments'),
    path('logistics/shipment/<int:pk>',views.LogisticsShipmentDetail.as_view(),name='LogisticsShipmentDetail'),
    path('logistics/shipment/<int:shipment_id>/update-status',views.LogisticsUpdateStatus.as_view(),name='LogisticsUpdateStatus'),
    path('logistics/delivery-tracking',views.LogisticsDeliveryTracking.as_view(),name='LogisticsDeliveryTracking'),
    path('logistics/reports',views.LogisticsReports.as_view(),name='LogisticsReports'),

    path('shipper/home',views.ShipperDashboard.as_view(),name='ShipperDashboard'),
    path('shipper/makeShipment',views.NewShipment.as_view(),name='NewShipment'),
    path('shipper/shipmentHistory',views.ShipmentHistory.as_view(),name='ShipmentHistory'),
    path('shipper/reports',views.ShipmentReports.as_view(),name='ShipperReports'),
    path('shipper/shipment/<int:pk>',views.ShipmentDetailView.as_view(),name="ShipperDetail"),

    path('authority/home',views.AuthorityDashboard.as_view(),name='AuthorityDashboard'),
    path('authority/listApprovals',views.AuthorityApproval.as_view(),name='AuthorityApprovals'),
    path('authority/request/<int:pk>',views.AuthorityRequestApproval.as_view(),name='AuthorityRequest'),
    path('authority/approve',views.AuthorityApproveRequest.as_view(),name='AuthorityApproved'),
    path('authority/shipment/<int:shipment_id>/approve',views.ShipmentApprovalView.as_view(),name='ShipmentApproval'),

    # Document Download URLs
    path('document/<int:document_id>/download',views.DownloadApprovalDocumentView.as_view(),name='DownloadDocument'),

    # Notification API URLs
    path('api/notifications/',views.NotificationAPIView.as_view(),name='NotificationAPI'),
    path('api/notifications/<int:notification_id>/mark-read/',views.MarkNotificationReadView.as_view(),name='MarkNotificationRead'),
    path('api/notifications/mark-all-read/',views.MarkAllNotificationsReadView.as_view(),name='MarkAllNotificationsRead'),
    path('api/notifications/unread-count/',views.NotificationUnreadCountView.as_view(),name='NotificationUnreadCount'),
]