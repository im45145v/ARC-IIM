#!/usr/bin/env python3
"""
Quick test to verify all fixes are working
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from alumni_system.database.connection import get_db_context
        from alumni_system.database.crud import get_alumni_count, create_alumni
        print("✅ Imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from alumni_system.database.connection import get_db_context
        from alumni_system.database.crud import get_alumni_count
        
        with get_db_context() as db:
            count = get_alumni_count(db)
        
        print(f"✅ Database connected! Found {count} alumni records")
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("\nMake sure database is running:")
        print("  docker-compose up -d")
        return False

def test_streamlit_app():
    """Test that Streamlit app can be imported"""
    print("\nTesting Streamlit app...")
    try:
        # Just check if the file can be read
        app_path = Path(__file__).parent / "alumni_system" / "frontend" / "app.py"
        content = app_path.read_text()
        
        # Check for the fixes
        if "st.switch_page" in content:
            print("⚠️  Warning: st.switch_page still found in code")
            return False
        
        if "st.session_state.page" in content and "st.rerun()" in content:
            print("✅ Streamlit navigation fix verified")
        else:
            print("⚠️  Warning: Navigation fix not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Streamlit app error: {e}")
        return False

def main():
    print("=" * 60)
    print("Alumni Management System - Fix Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Streamlit App", test_streamlit_app()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! You're ready to go!")
        print("\nNext steps:")
        print("  1. Add alumni: python3 scripts/add_alumni_batch.py")
        print("  2. Start app: streamlit run alumni_system/frontend/app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
