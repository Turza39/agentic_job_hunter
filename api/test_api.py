"""
Test script for the Agentic Job Hunter API
Run this after starting the API: python test_api.py
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "=" * 60)
    print("TEST: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✅ Health check passed")


def test_create_profile():
    """Test profile creation"""
    print("\n" + "=" * 60)
    print("TEST: Create Profile")
    print("=" * 60)
    
    profile_data = {
        "name": "John Doe",
        "email": f"john_{int(time.time())}@example.com",
        "phone": "+1-555-0123",
        "location": "San Francisco, CA",
        "salary_expectation": 150000,
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "github": "https://github.com/johndoe",
        "linkedin": "https://linkedin.com/in/johndoe",
        "portfolio": "https://johndoe.dev",
        "education": [
            {
                "school": "UC Berkeley",
                "degree": "BS Computer Science",
                "year": 2020
            }
        ],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Senior Backend Engineer",
                "years": 4
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/profiles", json=profile_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 201
    profile = response.json()
    print(f"✅ Profile created: {profile['id']}")
    
    return profile


def test_get_profile(profile_id):
    """Test getting a profile"""
    print("\n" + "=" * 60)
    print("TEST: Get Profile")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/profiles/{profile_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print(f"✅ Profile retrieved: {response.json()['name']}")


def test_list_profiles():
    """Test listing profiles"""
    print("\n" + "=" * 60)
    print("TEST: List Profiles")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/profiles?skip=0&limit=10")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Count: {len(data)}")
    print(f"First profile: {data[0] if data else 'None'}")
    
    assert response.status_code == 200
    print(f"✅ Listed {len(data)} profiles")


def test_update_profile(profile_id):
    """Test updating a profile"""
    print("\n" + "=" * 60)
    print("TEST: Update Profile")
    print("=" * 60)
    
    update_data = {
        "salary_expectation": 160000,
        "phone": "+1-555-9876"
    }
    
    response = requests.put(f"{BASE_URL}/api/profiles/{profile_id}", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print(f"✅ Profile updated")


def test_create_cv(profile_id):
    """Test CV upload"""
    print("\n" + "=" * 60)
    print("TEST: Upload CV")
    print("=" * 60)
    
    # Create a sample PDF file for testing
    sample_cv_path = Path("sample_resume.txt")
    sample_cv_path.write_text("This is a sample resume for testing.\n" * 20)
    
    with open(sample_cv_path, "rb") as f:
        files = {"file": (f.name, f, "text/plain")}
        data = {
            "category": "Backend",
            "target_roles": "Senior Engineer,Tech Lead",
            "skills": "Python,FastAPI,PostgreSQL"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/profiles/{profile_id}/cvs",
            files=files,
            data=data
        )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Clean up
    sample_cv_path.unlink()
    
    assert response.status_code == 201
    cv = response.json()
    print(f"✅ CV uploaded: {cv['id']}")
    
    return cv


def test_list_cvs(profile_id):
    """Test listing CVs for a profile"""
    print("\n" + "=" * 60)
    print("TEST: List CVs")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/profiles/{profile_id}/cvs")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Count: {len(data)}")
    for cv in data:
        print(f"  - {cv['filename']} ({cv['id']})")
    
    assert response.status_code == 200
    print(f"✅ Listed {len(data)} CVs")


def test_activate_cv(cv_id):
    """Test activating a CV"""
    print("\n" + "=" * 60)
    print("TEST: Activate CV")
    print("=" * 60)
    
    response = requests.post(f"{BASE_URL}/api/cvs/{cv_id}/activate")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print(f"✅ CV activated")


def test_create_preferences(profile_id):
    """Test creating preferences"""
    print("\n" + "=" * 60)
    print("TEST: Create User Preferences")
    print("=" * 60)
    
    pref_data = {
        "preferred_locations": ["San Francisco", "Los Angeles", "New York"],
        "exclude_locations": ["Remote"],
        "allow_remote": True,
        "allow_hybrid": True,
        "allow_onsite": True,
        "min_experience_years": 3,
        "max_experience_years": 20,
        "preferred_job_types": ["Full-time"],
        "min_salary": 140000,
        "max_salary": 200000,
        "required_keywords": ["Python", "Backend"],
        "excluded_keywords": ["PHP", "legacy"],
        "min_match_score": 75
    }
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/{profile_id}/preferences",
        json=pref_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 201
    print(f"✅ Preferences created")


def test_get_preferences(profile_id):
    """Test getting preferences"""
    print("\n" + "=" * 60)
    print("TEST: Get User Preferences")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/profiles/{profile_id}/preferences")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print(f"✅ Preferences retrieved")


def test_update_preferences(profile_id):
    """Test updating preferences"""
    print("\n" + "=" * 60)
    print("TEST: Update User Preferences")
    print("=" * 60)
    
    update_data = {
        "min_salary": 150000,
        "max_salary": 210000
    }
    
    response = requests.put(
        f"{BASE_URL}/api/profiles/{profile_id}/preferences",
        json=update_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print(f"✅ Preferences updated")


def test_delete_cv(cv_id):
    """Test deleting a CV"""
    print("\n" + "=" * 60)
    print("TEST: Delete CV")
    print("=" * 60)
    
    response = requests.delete(f"{BASE_URL}/api/cvs/{cv_id}")
    print(f"Status: {response.status_code}")
    
    assert response.status_code == 204
    print(f"✅ CV deleted")


def test_delete_profile(profile_id):
    """Test deleting a profile"""
    print("\n" + "=" * 60)
    print("TEST: Delete Profile")
    print("=" * 60)
    
    response = requests.delete(f"{BASE_URL}/api/profiles/{profile_id}")
    print(f"Status: {response.status_code}")
    
    assert response.status_code == 204
    print(f"✅ Profile deleted (soft delete)")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AGENTIC JOB HUNTER API - TEST SUITE")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Health check
        test_health_check()
        
        # Profile tests
        profile = test_create_profile()
        profile_id = profile["id"]
        
        test_get_profile(profile_id)
        test_list_profiles()
        test_update_profile(profile_id)
        
        # CV tests
        cv = test_create_cv(profile_id)
        cv_id = cv["id"]
        
        test_list_cvs(profile_id)
        test_activate_cv(cv_id)
        
        # Preferences tests
        test_create_preferences(profile_id)
        test_get_preferences(profile_id)
        test_update_preferences(profile_id)
        
        # Cleanup
        test_delete_cv(cv_id)
        test_delete_profile(profile_id)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to {BASE_URL}")
        print("Make sure the API is running:")
        print("  docker compose up api")
        raise


if __name__ == "__main__":
    run_all_tests()
