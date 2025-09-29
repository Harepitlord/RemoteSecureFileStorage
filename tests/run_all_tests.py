#!/usr/bin/env python3
"""
Test runner for all RemoteSecureFileStorage tests
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/hareeswaran/PycharmProjects/RemoteSecureFileStorage')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RemoteSecureFileStorage.settings')
django.setup()

from tests.test_encryption import run_standalone_tests as run_encryption_tests
from tests.test_vault_system import run_standalone_tests as run_vault_tests
import unittest


def main():
    """Run all test suites"""
    print("RemoteSecureFileStorage - Complete Test Suite")
    print("=" * 60)
    
    success_count = 0
    total_count = 4
    
    try:
        print("\n🔐 Running Encryption System Tests...")
        print("-" * 40)
        run_encryption_tests()
        success_count += 1
        print("✅ Encryption tests completed successfully")
    except Exception as e:
        print(f"❌ Encryption tests failed: {e}")
    
    try:
        print("\n🔒 Running Vault System Tests...")
        print("-" * 40)
        run_vault_tests()
        success_count += 1
        print("✅ Vault system tests completed successfully")
    except Exception as e:
        print(f"❌ Vault system tests failed: {e}")

    try:
        print("\n🏢 Running Hub App Tests...")
        print("-" * 40)
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('tests.test_hub')
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        if result.wasSuccessful():
            success_count += 1
            print("✅ Hub app tests completed successfully")
        else:
            print(f"❌ Hub app tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
    except Exception as e:
        print(f"❌ Hub app tests failed: {e}")

    try:
        print("\n👤 Running User Management Tests...")
        print("-" * 40)
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('tests.test_user_management')
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        if result.wasSuccessful():
            success_count += 1
            print("✅ User management tests completed successfully")
        else:
            print(f"❌ User management tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
    except Exception as e:
        print(f"❌ User management tests failed: {e}")

    print("\n" + "=" * 60)
    print(f"Test Summary: {success_count}/{total_count} test suites passed")
    
    if success_count == total_count:
        print("🎉 All tests passed! System is ready for production.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
