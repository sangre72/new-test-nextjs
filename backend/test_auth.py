"""
Test Authentication System
Quick validation script
"""
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

def test_password_hashing():
    """Test password hashing"""
    password = "Test123!"
    hashed = get_password_hash(password)

    print("✅ Password Hashing Test")
    print(f"   Original: {password}")
    print(f"   Hashed: {hashed[:50]}...")
    print(f"   Verify: {verify_password(password, hashed)}")
    print()

def test_jwt_tokens():
    """Test JWT token generation and verification"""
    payload = {
        "sub": "123",
        "email": "test@example.com",
        "tenant_id": 1
    }

    # Create tokens
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token({"sub": "123"})

    print("✅ JWT Token Test")
    print(f"   Access Token: {access_token[:50]}...")
    print(f"   Refresh Token: {refresh_token[:50]}...")

    # Decode access token
    decoded = decode_token(access_token)
    print(f"   Decoded sub: {decoded['sub']}")
    print(f"   Decoded email: {decoded['email']}")
    print(f"   Token type: {decoded['type']}")
    print()

def test_imports():
    """Test all auth-related imports"""
    print("✅ Import Test")

    try:
        from app.api.v1.endpoints.auth import router
        print("   ✅ auth endpoints imported")
    except Exception as e:
        print(f"   ❌ auth endpoints import failed: {e}")

    try:
        from app.schemas.auth import UserRegisterRequest, LoginResponse
        print("   ✅ auth schemas imported")
    except Exception as e:
        print(f"   ❌ auth schemas import failed: {e}")

    try:
        from app.api.deps import get_current_user, get_current_superuser
        print("   ✅ auth dependencies imported")
    except Exception as e:
        print(f"   ❌ auth dependencies import failed: {e}")

    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Authentication System Test")
    print("=" * 60)
    print()

    test_imports()
    test_password_hashing()
    test_jwt_tokens()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
