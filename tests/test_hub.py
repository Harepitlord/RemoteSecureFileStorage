"""
Test cases for Hub app functionality
"""
import os
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

# Setup Django for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RemoteSecureFileStorage.settings')
django.setup()

from Hub.models import Shipment, Ledger
from UserManagement.models import UserGroups

User = get_user_model()


class ShipmentModelTest(TestCase):
    """Test cases for Shipment model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role=UserGroups.shipper
        )
        
    def test_shipment_creation(self):
        """Test creating a shipment"""
        shipment = Shipment.objects.create(
            shipmentId='TEST-001',
            Shipper_Name='Test Shipper',
            Shipment_Company='Test Company',
            Receiver_Name='Test Receiver',
            Source='Mumbai',
            Destination='Delhi',
            Cargo_Name='Electronics',
            Cargo_Type='Fragile',
            created_by=self.user
        )
        
        self.assertEqual(shipment.shipmentId, 'TEST-001')
        self.assertEqual(shipment.status, Shipment.ShipmentStatus.DRAFT)
        self.assertEqual(shipment.created_by, self.user)
        
    def test_shipment_status_workflow(self):
        """Test shipment status transitions"""
        shipment = Shipment.objects.create(
            shipmentId='TEST-002',
            Shipper_Name='Test Shipper',
            Shipment_Company='Test Company',
            Receiver_Name='Test Receiver',
            Source='Mumbai',
            Destination='Delhi',
            Cargo_Name='Electronics',
            Cargo_Type='Fragile',
            created_by=self.user,
            status=Shipment.ShipmentStatus.DRAFT
        )
        
        # Test submission
        shipment.status = Shipment.ShipmentStatus.SUBMITTED
        shipment.save()
        self.assertEqual(shipment.status, Shipment.ShipmentStatus.SUBMITTED)
        
        # Test approval
        authority_user = User.objects.create_user(
            email='authority@example.com',
            password='testpass123',
            role=UserGroups.authority
        )
        
        shipment.status = Shipment.ShipmentStatus.APPROVED
        shipment.approved_by = authority_user
        shipment.approved_at = timezone.now()
        shipment.save()
        
        self.assertEqual(shipment.status, Shipment.ShipmentStatus.APPROVED)
        self.assertEqual(shipment.approved_by, authority_user)
        self.assertIsNotNone(shipment.approved_at)


class ShipmentViewTest(TestCase):
    """Test cases for Hub views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.shipper_user = User.objects.create_user(
            email='shipper@example.com',
            password='testpass123',
            role=UserGroups.shipper
        )
        self.authority_user = User.objects.create_user(
            email='authority@example.com',
            password='testpass123',
            role=UserGroups.authority
        )
        self.logistics_user = User.objects.create_user(
            email='logistics@example.com',
            password='testpass123',
            role=UserGroups.logistics
        )
        
    def test_shipper_dashboard_access(self):
        """Test shipper dashboard access"""
        self.client.login(email='shipper@example.com', password='testpass123')
        response = self.client.get(reverse('hub:ShipperDashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_authority_dashboard_access(self):
        """Test authority dashboard access"""
        self.client.login(email='authority@example.com', password='testpass123')
        response = self.client.get(reverse('hub:AuthorityDashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_logistics_dashboard_access(self):
        """Test logistics dashboard access"""
        self.client.login(email='logistics@example.com', password='testpass123')
        response = self.client.get(reverse('hub:LogisticsDashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_unauthorized_access(self):
        """Test unauthorized access to protected views"""
        # Test without login
        response = self.client.get(reverse('hub:ShipperDashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test wrong role access
        self.client.login(email='shipper@example.com', password='testpass123')
        response = self.client.get(reverse('hub:AuthorityDashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect due to insufficient permissions


class LedgerModelTest(TestCase):
    """Test cases for Ledger model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role=UserGroups.shipper
        )
        self.shipment = Shipment.objects.create(
            shipmentId='TEST-LEDGER-001',
            Shipper_Name='Test Shipper',
            Shipment_Company='Test Company',
            Receiver_Name='Test Receiver',
            Source='Mumbai',
            Destination='Delhi',
            Cargo_Name='Electronics',
            Cargo_Type='Fragile',
            created_by=self.user
        )
        
    def test_ledger_entry_creation(self):
        """Test creating a ledger entry"""
        ledger_entry = Ledger.objects.create(
            userId=self.user,
            shipment=self.shipment,
            event=Ledger.Events.CREATE,
            description='Shipment created'
        )
        
        self.assertEqual(ledger_entry.userId, self.user)
        self.assertEqual(ledger_entry.shipment, self.shipment)
        self.assertEqual(ledger_entry.event, Ledger.Events.CREATE)
        self.assertIsNotNone(ledger_entry.timestamp)
