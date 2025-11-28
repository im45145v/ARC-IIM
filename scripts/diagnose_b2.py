#!/usr/bin/env python3
"""
Diagnose B2 connection issues
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print("=" * 70)
print("B2 Diagnostic Tool")
print("=" * 70)
print()

# Check credentials
key_id = os.getenv('B2_APPLICATION_KEY_ID')
app_key = os.getenv('B2_APPLICATION_KEY')
bucket_name = os.getenv('B2_BUCKET_NAME')

print("1. Checking Credentials in .env")
print("-" * 70)
print(f"Key ID: {key_id}")
print(f"App Key: {app_key[:10]}...{app_key[-5:] if len(app_key) > 15 else ''}")
print(f"Bucket: {bucket_name}")
print()

if not key_id or not app_key or not bucket_name:
    print("❌ Missing credentials!")
    sys.exit(1)

print("✅ All credentials present")
print()

# Try to connect
print("2. Testing B2 Connection")
print("-" * 70)

try:
    from b2sdk.v2 import B2Api, InMemoryAccountInfo
    
    print("Attempting to authorize...")
    info = InMemoryAccountInfo()
    api = B2Api(info)
    
    try:
        api.authorize_account('production', key_id, app_key)
        print("✅ Authorization successful!")
        
        # Try to get bucket
        print()
        print("3. Checking Bucket Access")
        print("-" * 70)
        
        try:
            bucket = api.get_bucket_by_name(bucket_name)
            print(f"✅ Connected to bucket: {bucket.name}")
            print(f"   Bucket ID: {bucket.id_}")
            print(f"   Bucket Type: {bucket.type_}")
            
            # List files
            print()
            print("4. Listing Files in Bucket")
            print("-" * 70)
            
            files = []
            for file_version, _ in bucket.ls():
                files.append(file_version.file_name)
            
            print(f"✅ Bucket contains {len(files)} files")
            
            if files:
                print("\nRecent files:")
                for f in sorted(files, reverse=True)[:5]:
                    print(f"  - {f}")
            
            print()
            print("=" * 70)
            print("✅ B2 Configuration is WORKING!")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Bucket Error: {e}")
            print()
            print("Possible causes:")
            print("1. Bucket name is incorrect")
            print("2. Bucket doesn't exist")
            print("3. Application key doesn't have bucket access")
            print()
            print("Solution:")
            print("1. Check bucket name in B2 dashboard")
            print("2. Verify application key has 'readBuckets' capability")
            print("3. Try creating a new application key")
            
    except Exception as e:
        print(f"❌ Authorization Error: {e}")
        print()
        print("Possible causes:")
        print("1. Application Key ID is incorrect")
        print("2. Application Key is incorrect")
        print("3. Key has expired")
        print("4. Key was deleted or revoked")
        print("5. Key has been used and is no longer valid")
        print()
        print("Solution:")
        print("1. Go to B2 dashboard → Account → Application Keys")
        print("2. Check if the key still exists")
        print("3. If not, create a new application key")
        print("4. Copy the credentials exactly (no extra spaces)")
        print("5. Update .env file")
        print("6. Run this script again")
        
except ImportError:
    print("❌ b2sdk not installed")
    print("Install with: pip install b2sdk")

print()
