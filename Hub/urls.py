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
    path('shipper/shipment/<slug:ShipmentId>',views.ShipmentDetailView.as_view(),name="ShipperDetail"),
]