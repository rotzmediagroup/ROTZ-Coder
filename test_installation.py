#!/usr/bin/env python3
"""
DeepCode Installation Test Script

Run this script to verify that your DeepCode installation is working correctly.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Core dependencies
        import streamlit
        print("✅ Streamlit imported successfully")
        
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
        
        import bcrypt
        print("✅ bcrypt imported successfully")
        
        import cryptography
        print("✅ cryptography imported successfully")
        
        import pyotp
        print("✅ pyotp imported successfully")
        
        import qrcode
        print("✅ qrcode imported successfully")
        
        import jwt
        print("✅ PyJWT imported successfully")
        
        import requests
        print("✅ requests imported successfully")
        
        # Optional LLM dependencies
        try:
            import google.generativeai
            print("✅ Google Generative AI imported successfully")
        except ImportError:
            print("⚠️  Google Generative AI not available (optional)")
        
        # Custom modules
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from database.models import User, UserApiKey, init_database
        print("✅ Database models imported successfully")
        
        from auth.authentication import hash_password, verify_password
        print("✅ Authentication module imported successfully")
        
        from auth.encryption import encrypt_api_key, decrypt_api_key
        print("✅ Encryption module imported successfully")
        
        from providers.provider_factory import LLMProviderFactory
        print("✅ Provider factory imported successfully")
        
        from utils.database import get_db_session, init_database_tables
        print("✅ Database utilities imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_database():
    """Test database initialization"""
    print("\n🗄️  Testing database...")
    
    try:
        from utils.database import init_database_engine, get_db_session
        from database.models import User
        
        # Initialize database
        engine, Session = init_database_engine()
        print("✅ Database engine initialized")
        
        # Test session
        with get_db_session() as session:
            user_count = session.query(User).count()
            print(f"✅ Database connection successful - {user_count} users found")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def test_authentication():
    """Test authentication functions"""
    print("\n🔐 Testing authentication...")
    
    try:
        from auth.authentication import hash_password, verify_password, generate_totp_secret
        
        # Test password hashing
        password = "test_password"
        hashed = hash_password(password)
        
        if verify_password(password, hashed):
            print("✅ Password hashing/verification working")
        else:
            print("❌ Password verification failed")
            return False
        
        # Test TOTP secret generation
        secret = generate_totp_secret()
        if len(secret) == 32:
            print("✅ TOTP secret generation working")
        else:
            print("❌ TOTP secret generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False


def test_encryption():
    """Test API key encryption"""
    print("\n🔒 Testing encryption...")
    
    try:
        from auth.encryption import encrypt_api_key, decrypt_api_key
        
        # Test API key encryption/decryption
        api_key = "sk-test_api_key_1234567890"
        encrypted = encrypt_api_key(api_key)
        decrypted = decrypt_api_key(encrypted)
        
        if decrypted == api_key:
            print("✅ API key encryption/decryption working")
            return True
        else:
            print("❌ API key decryption failed")
            return False
            
    except Exception as e:
        print(f"❌ Encryption error: {e}")
        return False


def test_providers():
    """Test LLM providers"""
    print("\n🤖 Testing LLM providers...")
    
    try:
        from providers.provider_factory import LLMProviderFactory
        
        # Test provider factory
        providers = LLMProviderFactory.get_available_providers()
        print(f"✅ Available providers: {', '.join(providers)}")
        
        # Test provider info
        for provider in providers[:3]:  # Test first 3 providers
            info = LLMProviderFactory.get_provider_info(provider)
            print(f"✅ {provider}: {len(info.get('available_models', []))} models")
        
        return True
        
    except Exception as e:
        print(f"❌ Provider error: {e}")
        return False


def test_full_setup():
    """Test full database setup with super admin"""
    print("\n👑 Testing full setup...")
    
    try:
        from utils.database import init_database_tables, get_db_session
        from database.models import User
        
        # Initialize everything
        init_database_tables()
        print("✅ Database tables initialized")
        
        # Check super admin
        with get_db_session() as session:
            super_admin = session.query(User).filter_by(email="jerome@rotz.host").first()
            
            if super_admin and super_admin.is_super_admin:
                print("✅ Super admin account found")
                return True
            else:
                print("❌ Super admin account not found or not configured properly")
                return False
                
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False


def main():
    """Run all tests"""
    print("🧬 DeepCode Installation Test\n")
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Authentication", test_authentication),
        ("Encryption", test_encryption),
        ("Providers", test_providers),
        ("Full Setup", test_full_setup),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your DeepCode installation is ready.")
        print("\n🚀 Next steps:")
        print("1. Configure your secrets in .streamlit/secrets.toml")
        print("2. Run: streamlit run ui/streamlit_app.py")
        print("3. Open http://localhost:8501 in your browser")
        print("4. Login as jerome@rotz.host with password: ChangeMe123!")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that you're in the correct directory")
        print("3. Ensure Python path includes the current directory")
        
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)