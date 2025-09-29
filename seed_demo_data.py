#!/usr/bin/env python
"""
Demo Data Seeding Script for Remote Secure File Storage System
===============================================================
Creates realistic demo data for college project demonstration to reviewers.
Includes professional users, diverse international shipments, and realistic workflow scenarios.
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
from Hub.models import Shipment, ShipmentAssignment, Ledger
from UserManagement.models import UserGroups
from Cryptography.notifications import NotificationManager

User = get_user_model()

# Professional demo data configurations
COUNTRIES = [
    'United States', 'Canada', 'United Kingdom', 'Germany', 'France', 
    'Japan', 'Australia', 'Brazil', 'India', 'China', 'South Korea',
    'Netherlands', 'Sweden', 'Norway', 'Switzerland', 'Singapore'
]

CITIES = {
    'United States': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami', 'Seattle'],
    'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa', 'Edmonton'],
    'United Kingdom': ['London', 'Manchester', 'Birmingham', 'Glasgow', 'Liverpool', 'Bristol'],
    'Germany': ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt', 'Stuttgart'],
    'France': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Bordeaux'],
    'Japan': ['Tokyo', 'Osaka', 'Kyoto', 'Yokohama', 'Kobe', 'Nagoya'],
    'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Darwin'],
    'Brazil': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza', 'Recife'],
    'India': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad'],
    'China': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu', 'Hangzhou'],
    'South Korea': ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon', 'Gwangju'],
    'Netherlands': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven', 'Tilburg'],
    'Sweden': ['Stockholm', 'Gothenburg', 'Malmö', 'Uppsala', 'Västerås', 'Örebro'],
    'Norway': ['Oslo', 'Bergen', 'Trondheim', 'Stavanger', 'Drammen', 'Kristiansand'],
    'Switzerland': ['Zurich', 'Geneva', 'Basel', 'Bern', 'Lausanne', 'Winterthur'],
    'Singapore': ['Singapore City', 'Jurong', 'Woodlands', 'Tampines', 'Sengkang', 'Punggol']
}

CARGO_TYPES = [
    'Electronics', 'Pharmaceuticals', 'Automotive Parts', 'Medical Equipment',
    'Scientific Instruments', 'Computer Hardware', 'Precision Machinery',
    'Luxury Goods', 'Art & Collectibles', 'Chemicals', 'Textiles',
    'Food Products', 'Books & Documents', 'Jewelry', 'Raw Materials'
]

PROFESSIONAL_COMPANIES = [
    'TechCorp International', 'Global Pharmaceuticals Ltd', 'Precision Engineering Co',
    'Advanced Medical Systems', 'International Electronics Group', 'Luxury Brands Inc',
    'Scientific Solutions Ltd', 'Automotive Excellence Corp', 'Premium Textiles Co',
    'Global Food Industries', 'Elite Manufacturing', 'Innovation Labs Inc',
    'Professional Services Group', 'International Trade Corp', 'Excellence Logistics'
]

def create_demo_users():
    """Create professional demo users for different roles"""
    print("👥 Creating professional demo users...")
    
    users_created = {'authority': 0, 'logistics': 0, 'shipper': 0}
    
    # Create Authority users (Government/Customs officials)
    authority_users = [
        {'name': 'Dr. John Mitchell', 'email': 'j.mitchell@customs.gov', 'country': 'United States', 'title': 'Senior Customs Officer'},
        {'name': 'Sarah Thompson', 'email': 's.thompson@hmrc.gov.uk', 'country': 'United Kingdom', 'title': 'Border Control Supervisor'},
        {'name': 'Dr. Hans Weber', 'email': 'h.weber@zoll.de', 'country': 'Germany', 'title': 'Customs Authority Director'},
        {'name': 'Marie Dubois', 'email': 'm.dubois@douane.gouv.fr', 'country': 'France', 'title': 'Import/Export Specialist'},
        {'name': 'Kenji Nakamura', 'email': 'k.nakamura@customs.go.jp', 'country': 'Japan', 'title': 'Trade Compliance Officer'},
    ]
    
    for user_data in authority_users:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'name': user_data['name'],
                'role': UserGroups.authority,
                'country': user_data['country'],
                'phone_no': f"+{random.randint(1, 999)}{random.randint(1000000000, 9999999999)}"
            }
        )
        if created:
            user.set_password('demo2024!')
            user.save()
            users_created['authority'] += 1
    
    # Create Logistics users (Professional logistics companies)
    logistics_users = [
        {'name': 'Michael Rodriguez', 'email': 'm.rodriguez@globallogistics.com', 'country': 'United States', 'company': 'Global Logistics Solutions'},
        {'name': 'Emma Chen', 'email': 'e.chen@swiftcargo.ca', 'country': 'Canada', 'company': 'Swift Cargo Express'},
        {'name': 'David Williams', 'email': 'd.williams@premiumfreight.co.uk', 'country': 'United Kingdom', 'company': 'Premium Freight Services'},
        {'name': 'Anna Schmidt', 'email': 'a.schmidt@euroexpress.de', 'country': 'Germany', 'company': 'Euro Express Logistics'},
        {'name': 'Carlos Santos', 'email': 'c.santos@rapidtransport.com.br', 'country': 'Brazil', 'company': 'Rapid Transport Solutions'},
        {'name': 'Yuki Tanaka', 'email': 'y.tanaka@asiapacific.co.jp', 'country': 'Japan', 'company': 'Asia Pacific Logistics'},
        {'name': 'Sophie Anderson', 'email': 's.anderson@oceanicfreight.com.au', 'country': 'Australia', 'company': 'Oceanic Freight Services'},
    ]
    
    for user_data in logistics_users:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'name': user_data['name'],
                'role': UserGroups.logistics,
                'country': user_data['country'],
                'phone_no': f"+{random.randint(1, 999)}{random.randint(1000000000, 9999999999)}"
            }
        )
        if created:
            user.set_password('demo2024!')
            user.save()
            users_created['logistics'] += 1
    
    # Create Shipper users (Business professionals)
    shipper_users = [
        {'name': 'Robert Johnson', 'email': 'r.johnson@techcorp.com', 'country': 'United States', 'company': 'TechCorp International'},
        {'name': 'Jennifer Davis', 'email': 'j.davis@medicaldevices.ca', 'country': 'Canada', 'company': 'Advanced Medical Systems'},
        {'name': 'James Wilson', 'email': 'j.wilson@precisioneng.co.uk', 'country': 'United Kingdom', 'company': 'Precision Engineering Ltd'},
        {'name': 'Isabella Mueller', 'email': 'i.mueller@luxurybrands.de', 'country': 'Germany', 'company': 'European Luxury Brands'},
        {'name': 'Pierre Martin', 'email': 'p.martin@pharmaceuticals.fr', 'country': 'France', 'company': 'Global Pharmaceuticals'},
        {'name': 'Hiroshi Yamamoto', 'email': 'h.yamamoto@electronics.co.jp', 'country': 'Japan', 'company': 'Advanced Electronics Corp'},
        {'name': 'Olivia Thompson', 'email': 'o.thompson@scientificinst.com.au', 'country': 'Australia', 'company': 'Scientific Instruments Ltd'},
        {'name': 'Lucas Silva', 'email': 'l.silva@automotive.com.br', 'country': 'Brazil', 'company': 'Automotive Excellence'},
        {'name': 'Priya Patel', 'email': 'p.patel@textiles.co.in', 'country': 'India', 'company': 'Premium Textiles International'},
        {'name': 'Li Zhang', 'email': 'l.zhang@manufacturing.com.cn', 'country': 'China', 'company': 'Innovation Manufacturing'},
        {'name': 'Kim Min-jun', 'email': 'k.minjun@tech.co.kr', 'country': 'South Korea', 'company': 'Korean Tech Solutions'},
        {'name': 'Erik Larsson', 'email': 'e.larsson@nordic.se', 'country': 'Sweden', 'company': 'Nordic Industries'},
    ]
    
    for user_data in shipper_users:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'name': user_data['name'],
                'role': UserGroups.shipper,
                'country': user_data['country'],
                'phone_no': f"+{random.randint(1, 999)}{random.randint(1000000000, 9999999999)}"
            }
        )
        if created:
            user.set_password('demo2024!')
            user.save()
            users_created['shipper'] += 1
    
    print(f"   ✅ Created {users_created['authority']} authority users")
    print(f"   ✅ Created {users_created['logistics']} logistics users") 
    print(f"   ✅ Created {users_created['shipper']} shipper users")
    
    return users_created


def generate_professional_shipments():
    """Generate realistic professional shipment data for demo"""
    print("📦 Creating professional shipment data...")

    # Get users for assignments
    shippers = list(User.objects.filter(role=UserGroups.shipper))
    authorities = list(User.objects.filter(role=UserGroups.authority))
    logistics_users = list(User.objects.filter(role=UserGroups.logistics))

    if not shippers or not authorities:
        print("❌ No shipper or authority users found. Please create users first.")
        return []

    shipments_created = 0
    assignments_created = 0

    # Professional shipment scenarios
    shipment_scenarios = [
        # High-value electronics shipments
        {'cargo': 'Advanced Medical Imaging Equipment', 'type': 'Medical Equipment', 'value': 'High', 'priority': 'Urgent'},
        {'cargo': 'Quantum Computing Processors', 'type': 'Electronics', 'value': 'Very High', 'priority': 'Critical'},
        {'cargo': 'Precision Surgical Instruments', 'type': 'Medical Equipment', 'value': 'High', 'priority': 'High'},
        {'cargo': 'Pharmaceutical Research Samples', 'type': 'Pharmaceuticals', 'value': 'Critical', 'priority': 'Urgent'},
        {'cargo': 'Luxury Swiss Timepieces', 'type': 'Luxury Goods', 'value': 'Very High', 'priority': 'Standard'},
        {'cargo': 'Scientific Research Equipment', 'type': 'Scientific Instruments', 'value': 'High', 'priority': 'High'},
        {'cargo': 'Automotive Engine Components', 'type': 'Automotive Parts', 'value': 'Medium', 'priority': 'Standard'},
        {'cargo': 'Rare Earth Minerals', 'type': 'Raw Materials', 'value': 'High', 'priority': 'Standard'},
        {'cargo': 'Designer Fashion Collection', 'type': 'Textiles', 'value': 'High', 'priority': 'Standard'},
        {'cargo': 'Industrial Robotics Systems', 'type': 'Precision Machinery', 'value': 'Very High', 'priority': 'High'},
        {'cargo': 'Organic Chemical Compounds', 'type': 'Chemicals', 'value': 'Medium', 'priority': 'High'},
        {'cargo': 'Vintage Art Collection', 'type': 'Art & Collectibles', 'value': 'Very High', 'priority': 'Critical'},
        {'cargo': 'Semiconductor Wafers', 'type': 'Electronics', 'value': 'High', 'priority': 'Urgent'},
        {'cargo': 'Precision Optical Lenses', 'type': 'Scientific Instruments', 'value': 'High', 'priority': 'Standard'},
        {'cargo': 'Biotechnology Samples', 'type': 'Pharmaceuticals', 'value': 'Critical', 'priority': 'Critical'},
    ]

    # Create 25 diverse shipments
    for i in range(1, 26):
        # Select random scenario or create new one
        if i <= len(shipment_scenarios):
            scenario = shipment_scenarios[i-1]
        else:
            scenario = {
                'cargo': f'{random.choice(CARGO_TYPES)} Package {i}',
                'type': random.choice(CARGO_TYPES),
                'value': random.choice(['Medium', 'High', 'Very High']),
                'priority': random.choice(['Standard', 'High', 'Urgent'])
            }

        # Random source and destination countries (ensure different)
        source_country = random.choice(COUNTRIES)
        dest_country = random.choice([c for c in COUNTRIES if c != source_country])

        # Random cities from those countries
        source_city = random.choice(CITIES[source_country])
        dest_city = random.choice(CITIES[dest_country])

        # Random shipper and company
        shipper = random.choice(shippers)
        company = random.choice(PROFESSIONAL_COMPANIES)

        # Create shipment with realistic data
        shipment_data = {
            'shipmentId': f'DEMO-{2024}-{i:04d}',
            'Shipper_Name': shipper.name,
            'Shipment_Company': company,
            'Receiver_Name': f'Professional Receiver {i}',
            'Cargo_Name': scenario['cargo'],
            'Cargo_Type': scenario['type'],
            'Source': f'{source_city}, {source_country}',
            'Destination': f'{dest_city}, {dest_country}',
            'created_by': shipper,
            'status': 'SUBMITTED'
        }

        # Create shipment
        shipment, created = Shipment.objects.get_or_create(
            shipmentId=shipment_data['shipmentId'],
            defaults=shipment_data
        )

        if created:
            shipments_created += 1

            # Create ledger entry for shipment creation
            Ledger.objects.create(
                userId=shipper,
                shipmentId=shipment,
                event='CREATE'
            )

            # Determine approval status (70% approved, 20% rejected, 10% pending)
            approval_chance = random.random()
            authority = random.choice(authorities)

            if approval_chance < 0.7:  # 70% approved
                shipment.status = 'APPROVED'
                shipment.approved_by = authority
                shipment.approved_at = timezone.now() - timedelta(days=random.randint(1, 10))
                shipment.save()

                # Create approval ledger entry
                Ledger.objects.create(
                    userId=authority,
                    shipmentId=shipment,
                    event='APPROVED'
                )

                # Create logistics assignment for approved shipments
                if logistics_users and random.random() < 0.8:  # 80% of approved get assigned
                    logistics_user = random.choice(logistics_users)

                    assignment, assign_created = ShipmentAssignment.objects.get_or_create(
                        shipment=shipment,
                        logistics_user=logistics_user,
                        defaults={
                            'assigned_by': authority,
                            'status': random.choice(['ASSIGNED', 'IN_TRANSIT', 'DELIVERED']),
                            'notes': f'Professional logistics assignment for {scenario["priority"]} priority shipment'
                        }
                    )

                    if assign_created:
                        assignments_created += 1

                        # Set realistic dates based on status
                        if assignment.status in ['IN_TRANSIT', 'DELIVERED']:
                            assignment.pickup_date = timezone.now() - timedelta(days=random.randint(1, 5))
                        if assignment.status == 'DELIVERED':
                            assignment.delivery_date = timezone.now() - timedelta(days=random.randint(0, 3))
                        assignment.save()

                        # Create assignment ledger entry
                        Ledger.objects.create(
                            userId=authority,
                            shipmentId=shipment,
                            event='SHARED'
                        )

                        # Create status update entries
                        if assignment.status in ['IN_TRANSIT', 'DELIVERED']:
                            Ledger.objects.create(
                                userId=logistics_user,
                                shipmentId=shipment,
                                event='SHARED'
                            )

            elif approval_chance < 0.9:  # 20% rejected
                shipment.status = 'REJECTED'
                shipment.approved_by = authority
                shipment.approved_at = timezone.now() - timedelta(days=random.randint(1, 7))
                shipment.save()

                # Create rejection ledger entry (using available event types)
                Ledger.objects.create(
                    userId=authority,
                    shipmentId=shipment,
                    event='APPROVE_REQUEST'  # Using available event type
                )

            # 10% remain as SUBMITTED (pending review)

    print(f"   ✅ Created {shipments_created} professional shipments")
    print(f"   ✅ Created {assignments_created} logistics assignments")

    return shipments_created, assignments_created


def create_notifications():
    """Create realistic notifications for demo users"""
    print("🔔 Creating professional notifications...")

    notifications_created = 0

    # Get users
    authorities = list(User.objects.filter(role=UserGroups.authority))
    logistics_users = list(User.objects.filter(role=UserGroups.logistics))
    shippers = list(User.objects.filter(role=UserGroups.shipper))

    # Create notifications for shipments
    recent_shipments = Shipment.objects.all()[:10]
    for shipment in recent_shipments:
        NotificationManager.notify_shipment_created(shipment)
        notifications_created += 1

    # Create notifications for approved shipments
    approved_shipments = Shipment.objects.filter(status='APPROVED')[:5]
    for shipment in approved_shipments:
        NotificationManager.notify_shipment_approved(shipment)
        notifications_created += 1

    # Create notifications for rejected shipments
    rejected_shipments = Shipment.objects.filter(status='REJECTED')[:3]
    for shipment in rejected_shipments:
        NotificationManager.notify_shipment_rejected(shipment)
        notifications_created += 1

    # Create notifications for assignments
    recent_assignments = ShipmentAssignment.objects.all()[:5]
    for assignment in recent_assignments:
        NotificationManager.notify_assignment_updated(assignment)
        notifications_created += 1

    # Create key generation notifications
    for user in (authorities + logistics_users + shippers)[:5]:
        NotificationManager.notify_key_generation_required(user)
        notifications_created += 1

    print(f"   ✅ Created {notifications_created} professional notifications")

    return notifications_created


def main():
    """Main function to seed all demo data"""
    print("🎓 COLLEGE DEMO DATA SEEDING SCRIPT")
    print("=" * 60)
    print("Creating professional demo data for system review...")
    print()

    try:
        # Create users
        users_stats = create_demo_users()
        print()

        # Create shipments and assignments
        shipments_count, assignments_count = generate_professional_shipments()
        print()

        # Create notifications
        notifications_count = create_notifications()
        print()

        # Summary
        print("=" * 60)
        print("🎉 DEMO DATA CREATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)

        print("📊 Demo Data Summary:")
        print(f"   👥 Users Created:")
        print(f"      - Authority Users: {users_stats['authority']}")
        print(f"      - Logistics Users: {users_stats['logistics']}")
        print(f"      - Shipper Users: {users_stats['shipper']}")
        print(f"   📦 Shipments Created: {shipments_count}")
        print(f"   🚚 Logistics Assignments: {assignments_count}")
        print(f"   🔔 Notifications Created: {notifications_count}")
        print()

        print("🔐 Demo Login Credentials:")
        print("   Password for all users: demo2024!")
        print()
        print("   Authority Users:")
        print("   - j.mitchell@customs.gov (US Customs)")
        print("   - s.thompson@hmrc.gov.uk (UK Border Control)")
        print()
        print("   Logistics Users:")
        print("   - m.rodriguez@globallogistics.com (Global Logistics)")
        print("   - e.chen@swiftcargo.ca (Swift Cargo)")
        print()
        print("   Shipper Users:")
        print("   - r.johnson@techcorp.com (TechCorp International)")
        print("   - j.davis@medicaldevices.ca (Medical Devices)")
        print()

        print("🚀 System Ready for Demo!")
        print("   - Diverse international shipments across 16 countries")
        print("   - Realistic approval/rejection workflow")
        print("   - Active logistics assignments with status tracking")
        print("   - Professional notifications and activity logs")
        print("   - Complete audit trail in ledger system")

        return True

    except Exception as e:
        print(f"❌ Error during demo data creation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
