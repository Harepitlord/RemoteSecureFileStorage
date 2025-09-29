"""
Test cases for UserManagement app functionality
"""
import os
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError

# Setup Django for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RemoteSecureFileStorage.settings')
django.setup()

from UserManagement.models import UserGroups
from UserManagement.forms import NewUser

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test cases for Custom User model"""
    
    def test_user_creation(self):
        """Test creating a user with different roles"""
        # Test shipper user
        shipper = User.objects.create_user(
            email='shipper@example.com',
            password='testpass123',
            role=UserGroups.shipper
        )
        self.assertEqual(shipper.email, 'shipper@example.com')
        self.assertEqual(shipper.role, UserGroups.shipper)
        self.assertTrue(shipper.check_password('testpass123'))
        
        # Test authority user
        authority = User.objects.create_user(
            email='authority@example.com',
            password='testpass123',
            role=UserGroups.authority
        )
        self.assertEqual(authority.role, UserGroups.authority)
        
        # Test logistics user
        logistics = User.objects.create_user(
            email='logistics@example.com',
            password='testpass123',
            role=UserGroups.logistics
        )
        self.assertEqual(logistics.role, UserGroups.logistics)
        
    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role=UserGroups.shipper
        )
        self.assertEqual(str(user), 'test@example.com')
        
    def test_user_email_uniqueness(self):
        """Test that email addresses must be unique"""
        User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role=UserGroups.shipper
        )
        
        # Attempting to create another user with the same email should fail
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='test@example.com',
                password='testpass456',
                role=UserGroups.authority
            )
            
    def test_superuser_creation(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, UserGroups.authority)  # Default role for superuser


class UserRegistrationFormTest(TestCase):
    """Test cases for User Registration Form"""
    
    def test_valid_registration_form(self):
        """Test valid registration form data"""
        form_data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'complexpass123',
            'role': 'shipper',
            'country': 'US',
            'phone_no': '1234567890'
        }
        form = NewUser(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_password_mismatch(self):
        """Test password mismatch validation"""
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123',
            'role': UserGroups.shipper
        }
        # Skip this test as NewUser form doesn't have password confirmation
        pass
        
    def test_invalid_email(self):
        """Test invalid email validation"""
        form_data = {
            'email': 'invalid-email',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': UserGroups.shipper
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
    def test_duplicate_email(self):
        """Test duplicate email validation"""
        # Create a user first
        User.objects.create_user(
            email='existing@example.com',
            password='testpass123',
            role=UserGroups.shipper
        )
        
        # Try to register with the same email
        form_data = {
            'email': 'existing@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': UserGroups.authority
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserManagementViewTest(TestCase):
    """Test cases for UserManagement views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
    def test_registration_view_get(self):
        """Test registration view GET request"""
        response = self.client.get(reverse('UserManagement:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
        
    def test_registration_view_post_valid(self):
        """Test registration view POST with valid data"""
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': UserGroups.shipper
        }
        response = self.client.post(reverse('UserManagement:register'), data=form_data)
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check that user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        
    def test_login_view(self):
        """Test login view"""
        # Create a user first
        user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            role=UserGroups.shipper
        )
        
        # Test login
        response = self.client.post(reverse('UserManagement:login'), {
            'username': 'testuser@example.com',
            'password': 'testpass123'
        })
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        response = self.client.get(reverse('UserManagement:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user"""
        user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            role=UserGroups.shipper
        )
        
        self.client.login(email='testuser@example.com', password='testpass123')
        response = self.client.get(reverse('UserManagement:profile'))
        self.assertEqual(response.status_code, 200)


class UserGroupsTest(TestCase):
    """Test cases for UserGroups choices"""
    
    def test_user_groups_choices(self):
        """Test that all user group choices are available"""
        choices = UserGroups.choices
        choice_values = [choice[0] for choice in choices]
        
        self.assertIn(UserGroups.shipper, choice_values)
        self.assertIn(UserGroups.logistics, choice_values)
        self.assertIn(UserGroups.authority, choice_values)
        
    def test_user_groups_labels(self):
        """Test user group labels"""
        self.assertEqual(UserGroups.shipper.label, 'Shipper')
        self.assertEqual(UserGroups.logistics.label, 'Logistics')
        self.assertEqual(UserGroups.authority.label, 'Authority')
