#!/usr/bin/env python3
"""
Setup script for Backblaze B2 storage configuration
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_b2():
    """Interactive B2 setup"""
    
    print("=" * 70)
    print("Backblaze B2 Setup")
    print("=" * 70)
    print()
    
    print("This script will help you configure Backblaze B2 storage.")
    print()
    print("Prerequisites:")
    print("1. Create a Backblaze B2 account at https://www.backblaze.com/b2/")
    print("2. Create an application key in B2 dashboard")
    print("3. Create a bucket for storing LinkedIn PDFs")
    print()
    
    # Get credentials
    print("Enter your B2 credentials:")
    print()
    
    key_id = input("B2 Application Key ID: ").strip()
    if not key_id:
        print("❌ Application Key ID is required")
        return False
    
    app_key = input("B2 Application Key: ").strip()
    if not app_key:
        print("❌ Application Key is required")
        return False
    
    bucket_name = input("B2 Bucket Name: ").strip()
    if not bucket_name:
        print("❌ Bucket Name is required")
        return False
    
    print()
    print("Testing credentials...")
    print()
    
    # Test credentials
    try:
        from b2sdk.v2 import B2Api, InMemoryAccountInfo
        
        info = InMemoryAccountInfo()
        api = B2Api(info)
        api.authorize_account("production", key_id, app_key)
        
        # Try to get bucket
        bucket = api.get_bucket_by_name(bucket_name)
        
        print("✅ B2 credentials are valid!")
        print(f"✅ Connected to bucket: {bucket.name}")
        print()
        
        # Show how to update .env
        print("Update your .env file with:")
        print()
        print(f"B2_APPLICATION_KEY_ID={key_id}")
        print(f"B2_APPLICATION_KEY={app_key}")
        print(f"B2_BUCKET_NAME={bucket_name}")
        print()
        
        # Ask to update .env
        update = input("Would you like me to update .env file? (y/n): ").strip().lower()
        
        if update == 'y':
            env_file = Path(__file__).parent.parent / '.env'
            
            # Read current .env
            content = env_file.read_text()
            
            # Update B2 settings
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                if line.startswith('B2_APPLICATION_KEY_ID='):
                    new_lines.append(f'B2_APPLICATION_KEY_ID={key_id}')
                elif line.startswith('B2_APPLICATION_KEY='):
                    new_lines.append(f'B2_APPLICATION_KEY={app_key}')
                elif line.startswith('B2_BUCKET_NAME='):
                    new_lines.append(f'B2_BUCKET_NAME={bucket_name}')
                else:
                    new_lines.append(line)
            
            # Write back
            env_file.write_text('\n'.join(new_lines))
            
            print("✅ .env file updated!")
            print()
            print("You can now use B2 storage for LinkedIn PDFs.")
            
        return True
        
    except Exception as e:
        print(f"❌ B2 credentials are invalid: {e}")
        print()
        print("Please check:")
        print("1. Application Key ID is correct")
        print("2. Application Key is correct")
        print("3. Bucket name exists and is accessible")
        print("4. Your B2 account is active")
        print()
        return False


def test_b2():
    """Test existing B2 configuration"""
    
    print("=" * 70)
    print("Testing B2 Configuration")
    print("=" * 70)
    print()
    
    try:
        from alumni_system.storage.b2_client import get_storage_client
        
        print("Initializing B2 client...")
        client = get_storage_client()
        
        print("✅ B2 client initialized")
        print()
        
        print("Connecting to bucket...")
        bucket = client._get_bucket()
        
        print(f"✅ Connected to bucket: {bucket.name}")
        print()
        
        print("Listing files...")
        files = []
        for file_version, _ in bucket.ls():
            files.append(file_version.file_name)
        
        print(f"✅ Bucket contains {len(files)} files")
        print()
        
        # Show LinkedIn profile PDFs
        pdf_files = [f for f in files if 'linkedin_profiles' in f]
        print(f"LinkedIn PDFs in bucket: {len(pdf_files)}")
        
        if pdf_files:
            print()
            print("Recent PDFs:")
            for f in sorted(pdf_files, reverse=True)[:5]:
                print(f"  - {f}")
        
        print()
        print("✅ B2 configuration is working!")
        return True
        
    except Exception as e:
        print(f"❌ B2 Error: {e}")
        print()
        print("Your B2 credentials may be invalid.")
        print("Run: python3 scripts/setup_b2.py")
        print()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Backblaze B2 Setup")
    parser.add_argument("--setup", action="store_true", help="Setup B2 credentials")
    parser.add_argument("--test", action="store_true", help="Test B2 configuration")
    
    args = parser.parse_args()
    
    if args.setup:
        success = setup_b2()
        sys.exit(0 if success else 1)
    elif args.test:
        success = test_b2()
        sys.exit(0 if success else 1)
    else:
        # Default: test first, then offer setup
        print("Checking B2 configuration...")
        print()
        
        if test_b2():
            print()
            print("To update credentials, run:")
            print("  python3 scripts/setup_b2.py --setup")
        else:
            print()
            print("Would you like to setup B2 now? (y/n): ", end="")
            if input().strip().lower() == 'y':
                setup_b2()
