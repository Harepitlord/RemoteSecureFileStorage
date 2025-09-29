#!/usr/bin/env python
"""
Data seeding script for Remote Secure File Storage system
Creates test users and shipments with realistic data distribution
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RemoteSecureFileStorage.settings')
django.setup()

from django.contrib.auth import get_user_model
from Hub.models import Shipment, ShipmentAssignment
from UserManagement.models import UserGroups
from Cryptography.notifications import NotificationManager

User = get_user_model()

# Test data configurations
COUNTRIES = [
    'United States', 'Canada', 'United Kingdom', 'Germany', 'France', 
    'Japan', 'Australia', 'Brazil', 'India', 'China', 'South Korea',
    'Netherlands', 'Sweden', 'Norway', 'Switzerland', 'Singapore'
]

CITIES = {
    'United States': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'],
    'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa', 'Edmonton'],
    'United Kingdom': ['London', 'Manchester', 'Birmingham', 'Glasgow', 'Liverpool', 'Bristol'],
    'Germany': ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt', 'Stuttgart'],
    'France': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes'],
    'Japan': ['Tokyo', 'Osaka', 'Kyoto', 'Yokohama', 'Kobe', 'Nagoya'],
    'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Canberra'],
    'Brazil': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza', 'Belo Horizonte'],
    'India': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad'],
    'China': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu', 'Hangzhou'],
    'South Korea': ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon', 'Gwangju'],
    'Netherlands': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven', 'Groningen'],
    'Sweden': ['Stockholm', 'Gothenburg', 'Malmö', 'Uppsala', 'Västerås', 'Örebro'],
    'Norway': ['Oslo', 'Bergen', 'Trondheim', 'Stavanger', 'Drammen', 'Fredrikstad'],
    'Switzerland': ['Zurich', 'Geneva', 'Basel', 'Bern', 'Lausanne', 'Winterthur'],
    'Singapore': ['Singapore City', 'Jurong', 'Woodlands', 'Tampines', 'Sengkang', 'Punggol']
}

CARGO_TYPES = [
    'Electronics', 'Pharmaceuticals', 'Automotive Parts', 'Textiles', 'Food Products',
    'Chemicals', 'Machinery', 'Medical Equipment', 'Books & Documents', 'Jewelry',
    'Art & Antiques', 'Scientific Instruments', 'Computer Hardware', 'Clothing',
    'Furniture', 'Raw Materials', 'Consumer Goods', 'Industrial Equipment'
]

COMPANY_NAMES = [
    'Global Logistics Corp', 'International Shipping Ltd', 'WorldWide Transport',
    'Express Cargo Solutions', 'Premium Freight Services', 'Secure Transport Inc',
    'Elite Shipping Company', 'Advanced Logistics Group', 'Swift Cargo Express',
    'Professional Transport Co', 'Reliable Shipping Services', 'Fast Track Logistics',
    'Global Express Network', 'Secure Freight Solutions', 'International Cargo Hub'
]

def create_users():
    """Create test users for different roles"""
    print("👥 Creating test users...")
    
    users_created = {'authority': 0, 'logistics': 0, 'shipper': 0}
    
    # Create Authority users
    authority_users = [
        {'name': 'John Authority', 'email': 'john.authority@gov.com', 'country': 'United States'},
        {'name': 'Sarah Wilson', 'email': 'sarah.wilson@customs.uk', 'country': 'United Kingdom'},
        {'name': 'Hans Mueller', 'email': 'hans.mueller@zoll.de', 'country': 'Germany'},
        {'name': 'Marie Dubois', 'email': 'marie.dubois@douane.fr', 'country': 'France'},
    ]
    
    for user_data in authority_users:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'name': user_data['name'],
                'role': UserGroups.authority,
                'country': user_data['country'],
                'phone_no': f"+1{random.randint(1000000000, 9999999999)}"
            }
        )
        if created:
            user.set_password('authority123')
            user.save()
            users_created['authority'] += 1
    
    # Create Logistics users
    logistics_users = [
        {'name': 'Mike Transport', 'email': 'mike.transport@logistics.com', 'country': 'United States'},
        {'name': 'Lisa Delivery', 'email': 'lisa.delivery@fastship.com', 'country': 'Canada'},
        {'name': 'David Cargo', 'email': 'david.cargo@globallog.uk', 'country': 'United Kingdom'},
        {'name': 'Anna Freight', 'email': 'anna.freight@euroship.de', 'country': 'Germany'},
        {'name': 'Carlos Express', 'email': 'carlos.express@rapidlog.br', 'country': 'Brazil'},
        {'name': 'Yuki Logistics', 'email': 'yuki.logistics@japanship.jp', 'country': 'Japan'},
    ]
    
    for user_data in logistics_users:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'name': user_data['name'],
                'role': UserGroups.logistics,
                'country': user_data['country'],
                'phone_no': f"+1{random.randint(1000000000, 9999999999)}"
            }
        )
        if created:
            user.set_password('logistics123')
            user.save()
            users_created['logistics'] += 1
    
    # Create Shipper users
    shipper_users = [
        {'name': 'Robert Smith', 'email': 'robert.smith@techcorp.com', 'country': 'United States'},
        {'name': 'Emma Johnson', 'email': 'emma.johnson@pharmatech.ca', 'country': 'Canada'},
        {'name': 'James Brown', 'email': 'james.brown@autoparts.uk', 'country': 'United Kingdom'},
        {'name': 'Sophie Martin', 'email': 'sophie.martin@luxurygoods.fr', 'country': 'France'},
        {'name': 'Klaus Weber', 'email': 'klaus.weber@machinery.de', 'country': 'Germany'},
        {'name': 'Hiroshi Tanaka', 'email': 'hiroshi.tanaka@electronics.jp', 'country': 'Japan'},
        {'name': 'Olivia Wilson', 'email': 'olivia.wilson@medequip.au', 'country': 'Australia'},
        {'name': 'Pedro Silva', 'email': 'pedro.silva@textiles.br', 'country': 'Brazil'},
        {'name': 'Priya Sharma', 'email': 'priya.sharma@spices.in', 'country': 'India'},
        {'name': 'Li Wei', 'email': 'li.wei@manufacturing.cn', 'country': 'China'},
    ]
    
    for user_data in shipper_users:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'name': user_data['name'],
                'role': UserGroups.shipper,
                'country': user_data['country'],
                'phone_no': f"+1{random.randint(1000000000, 9999999999)}"
            }
        )
        if created:
            user.set_password('shipper123')
            user.save()
            users_created['shipper'] += 1
    
    print(f"   ✅ Created {users_created['authority']} authority users")
    print(f"   ✅ Created {users_created['logistics']} logistics users") 
    print(f"   ✅ Created {users_created['shipper']} shipper users")
    
    return users_created

def generate_shipment_data():
    """Generate realistic shipment data"""
    shipments_data = []
    
    # Get users for assignments
    shippers = list(User.objects.filter(role=UserGroups.shipper))
    authorities = list(User.objects.filter(role=UserGroups.authority))
    logistics_users = list(User.objects.filter(role=UserGroups.logistics))
    
    if not shippers or not authorities:
        print("❌ No shipper or authority users found. Please create users first.")
        return []
    
    for i in range(1, 31):  # Create 30 shipments
        # Random source and destination countries
        source_country = random.choice(COUNTRIES)
        dest_country = random.choice([c for c in COUNTRIES if c != source_country])
        
        # Random cities from those countries
        source_city = random.choice(CITIES[source_country])
        dest_city = random.choice(CITIES[dest_country])
        
        # Random cargo and company
        cargo_type = random.choice(CARGO_TYPES)
        company = random.choice(COMPANY_NAMES)
        
        # Random shipper
        shipper = random.choice(shippers)
        
        # Generate shipment data
        shipment_data = {
            'shipmentId': f'SHP-{2024}-{i:04d}',
            'Shipper_Name': shipper.name,
            'Shipment_Company': company,
            'Receiver_Name': f'Receiver {i}',
            'Cargo_Name': f'{cargo_type} Package {i}',
            'Cargo_Type': cargo_type,
            'Source': f'{source_city}, {source_country}',
            'Destination': f'{dest_city}, {dest_country}',
            'created_by': shipper,
            'status': 'SUBMITTED'  # Will be updated based on approval
        }
        
        shipments_data.append(shipment_data)
    
    return shipments_data
