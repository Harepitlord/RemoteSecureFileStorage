from django.urls import path

from Hub import views

app_name='hub'
urlpatterns = [
    path('',views.Home.as_view(),name='Home'),
    path('home',views.DashBoard.as_view(),name='Dashboard'),
    path('about',views.About.as_view(),name='About'),

    path('logistics/home',views.LogisticsDashboard.as_view(),name='LogisticsDashboard'),

    path('shipper/home',views.ShipperDashboard.as_view(),name='ShipperDashboard'),
    path('shipper/makeShipment',views.NewShipment.as_view(),name='NewShipment'),
    path('shipper/shipmentHistory',views.ShipmentHistory.as_view(),name='ShipmentHistory'),
    path('shipper/reports',views.ShipmentReports.as_view(),name='ShipperReports'),
    path('shipper/shipment/<int:pk>',views.ShipmentDetailView.as_view(),name="ShipperDetail"),

    path('authority/home',views.AuthorityDashboard.as_view(),name='AuthorityDashboard'),
    path('authority/listApprovals',views.AuthorityApproval.as_view(),name='AuthorityApprovals'),
    path('authority/request/<int:pk>',views.AuthorityRequestApproval.as_view(),name='AuthorityRequest'),
    path('authority/approve',views.AuthorityApproveRequest.as_view(),name='AuthorityApproved'),
]