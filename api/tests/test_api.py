"""
Integration test script for the Agentic Job Hunter API.

Run the API first, then from the project root:

    python -m api.tests.test_api

Or from the api/ directory:

    cd api && python -m tests.test_api
"""

import requests
import json
import time
from pathlib import Path


BASE_URL = "http://localhost:8000"


# ============================================================================
# Utility
# ============================================================================

def print_section(title):
    print("\n" + "=" * 60)
    print(f"TEST: {title}")
    print("=" * 60)


# ============================================================================
# Health
# ============================================================================

def test_health_check():
    """Test health check endpoint."""

    print_section("Health Check")

    response = requests.get(f"{BASE_URL}/health")

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    print("✅ Health check passed")


# ============================================================================
# Profile
# ============================================================================

def test_create_profile():
    """Test profile creation."""

    print_section("Create Profile")

    profile_data = {
        "name": "John Doe",
        "email": f"john_{int(time.time())}@example.com",
        "phone": "+1-555-0123",
        "location": "San Francisco, CA",
        "salary_expectation": 150000,
        "skills": [
            "Python",
            "FastAPI",
            "PostgreSQL",
            "Docker"
        ],
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

    response = requests.post(
        f"{BASE_URL}/api/profiles",
        json=profile_data
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 201

    profile = response.json()

    print(f"✅ Profile created: {profile['id']}")

    return profile


def test_get_profile(profile_id):
    """Test getting a profile."""

    print_section("Get Profile")

    response = requests.get(
        f"{BASE_URL}/api/profiles/{profile_id}"
    )

    assert response.status_code == 200

    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print(f"✅ Profile retrieved")


def test_list_profiles():
    """Test listing profiles."""

    print_section("List Profiles")

    response = requests.get(
        f"{BASE_URL}/api/profiles?skip=0&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    print(f"Count: {len(data)}")
    print(f"First profile: {data[0] if data else 'None'}")

    print(f"✅ Listed {len(data)} profiles")


def test_update_profile(profile_id):
    """Test updating a profile."""

    print_section("Update Profile")

    update_data = {
        "salary_expectation": 160000,
        "phone": "+1-555-9876"
    }

    response = requests.put(
        f"{BASE_URL}/api/profiles/{profile_id}",
        json=update_data
    )

    assert response.status_code == 200

    print("✅ Profile updated")


# ============================================================================
# CV
# ============================================================================

def test_create_cv(profile_id):
    """Test CV upload."""

    print_section("Upload CV")

    sample_cv_path = Path("sample_resume.pdf")

    sample_cv_path.write_text(
        "This is a sample resume for testing.\n" * 20
    )

    try:
        with open(sample_cv_path, "rb") as f:
            files = {
                "file": (
                    f.name,
                    f,
                    "application/pdf"
                )
            }

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

    finally:
        if sample_cv_path.exists():
            sample_cv_path.unlink()

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 201

    cv = response.json()

    print(f"✅ CV uploaded: {cv['id']}")

    return cv


def test_list_cvs(profile_id):
    """Test listing CVs."""

    print_section("List CVs")

    response = requests.get(
        f"{BASE_URL}/api/profiles/{profile_id}/cvs"
    )

    assert response.status_code == 200

    data = response.json()

    print(f"Count: {len(data)}")

    for cv in data:
        print(f"  - {cv['filename']} ({cv['id']})")

    print(f"✅ Listed {len(data)} CVs")


def test_activate_cv(cv_id):
    """Test activating a CV."""

    print_section("Activate CV")

    response = requests.post(
        f"{BASE_URL}/api/cvs/{cv_id}/activate"
    )

    assert response.status_code == 200

    print("✅ CV activated")


def test_delete_cv(cv_id):
    """Test deleting a CV."""

    print_section("Delete CV")

    response = requests.delete(
        f"{BASE_URL}/api/cvs/{cv_id}"
    )

    assert response.status_code == 204

    print("✅ CV deleted")


# ============================================================================
# Preferences
# ============================================================================

def test_create_preferences(profile_id):
    """Test creating preferences."""

    print_section("Create User Preferences")

    pref_data = {
        "preferred_locations": [
            "San Francisco",
            "Los Angeles",
            "New York"
        ],
        "exclude_locations": [
            "Remote"
        ],
        "allow_remote": True,
        "allow_hybrid": True,
        "allow_onsite": True,
        "min_experience_years": 3,
        "max_experience_years": 20,
        "preferred_job_types": [
            "Full-time"
        ],
        "min_salary": 140000,
        "max_salary": 200000,
        "required_keywords": [
            "Python",
            "Backend"
        ],
        "excluded_keywords": [
            "PHP",
            "legacy"
        ],
        "min_match_score": 75
    }

    response = requests.post(
        f"{BASE_URL}/api/profiles/{profile_id}/preferences",
        json=pref_data
    )

    assert response.status_code == 201

    print("✅ Preferences created")


def test_get_preferences(profile_id):
    """Test getting preferences."""

    print_section("Get User Preferences")

    response = requests.get(
        f"{BASE_URL}/api/profiles/{profile_id}/preferences"
    )

    assert response.status_code == 200

    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("✅ Preferences retrieved")


def test_update_preferences(profile_id):
    """Test updating preferences."""

    print_section("Update User Preferences")

    update_data = {
        "min_salary": 150000,
        "max_salary": 210000
    }

    response = requests.put(
        f"{BASE_URL}/api/profiles/{profile_id}/preferences",
        json=update_data
    )

    assert response.status_code == 200

    print("✅ Preferences updated")


# ============================================================================
# Company
# ============================================================================

def test_company_endpoints():
    """
    Test company endpoints.

    Note:
    The career_page_url is stored on the Company row itself.
    No separate JobSource row is created.
    """

    print_section("Company")

    company_data = {
        "name": f"Test Company {int(time.time())}",
        "website": "https://testcompany.com",
        "career_page_url": "https://testcompany.com/careers",
        "description": "A test company",
        "industry": "Software",
        "country": "United States"
    }

    # ------------------------------------------------------------------
    # Create company
    # ------------------------------------------------------------------

    response = requests.post(
        f"{BASE_URL}/api/companies",
        json=company_data
    )

    assert response.status_code == 201

    company = response.json()
    company_id = company["id"]

    print(f"✅ Company created: {company_id}")

    # Make sure removed logo_url is not required.
    assert "logo_url" not in company

    # ------------------------------------------------------------------
    # Get company
    # ------------------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/api/companies/{company_id}"
    )

    assert response.status_code == 200

    fetched_company = response.json()

    assert fetched_company["id"] == company_id
    assert fetched_company["name"] == company_data["name"]
    assert fetched_company["career_page_url"] == (
        company_data["career_page_url"]
    )

    print("✅ Company retrieved")

    # ------------------------------------------------------------------
    # List companies
    # ------------------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/api/companies"
    )

    assert response.status_code == 200
    assert len(response.json()) > 0

    print("✅ Companies listed")

    # ------------------------------------------------------------------
    # Update company
    # ------------------------------------------------------------------

    update_data = {
        "description": "Updated Description"
    }

    response = requests.put(
        f"{BASE_URL}/api/companies/{company_id}",
        json=update_data
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Updated Description"

    print("✅ Company updated")

    return company_id


# ============================================================================
# Jobs
# ============================================================================

def test_job_endpoints(company_id):
    """
    Test job ingestion and deduplication.

    In the real system, n8n will discover jobs and call POST /jobs.
    The user does not manually create these jobs.
    """

    print_section("Jobs")

    job_data = {
        "company_id": company_id,
        "title": "Backend Python Developer",
        "description": "Develop APIs using Python and FastAPI.",
        "location": "San Francisco, CA",
        "job_type": "Full-time",
        "remote_type": "remote",
        "salary_min": 100000,
        "salary_max": 140000,
        "experience_level": "Mid-level",
        "requirements": [
            "Python",
            "FastAPI",
            "PostgreSQL"
        ],
        "nice_to_have": [
            "Docker"
        ],
        "application_url": (
            "https://testcompany.com/careers/apply/1"
        )
    }

    # ------------------------------------------------------------------
    # Ingest job
    # ------------------------------------------------------------------

    response = requests.post(
        f"{BASE_URL}/api/jobs",
        json=job_data
    )

    assert response.status_code == 201

    job = response.json()
    job_id = job["id"]

    print(f"✅ Job ingested: {job_id}")

    # ------------------------------------------------------------------
    # Verify job data
    # ------------------------------------------------------------------

    assert job["company_id"] == company_id
    assert job["title"] == job_data["title"]
    assert job["description"] == job_data["description"]

    assert job["normalized_hash"] is not None

    print(
        f"✅ Job hash generated: "
        f"{job['normalized_hash']}"
    )

    # ------------------------------------------------------------------
    # Duplicate job
    # ------------------------------------------------------------------

    response = requests.post(
        f"{BASE_URL}/api/jobs",
        json=job_data
    )

    assert response.status_code == 201

    duplicate_response = response.json()

    assert duplicate_response["id"] == job_id

    print(
        "✅ Duplicate job handled correctly "
        "(existing job returned)"
    )

    # ------------------------------------------------------------------
    # Get job
    # ------------------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/api/jobs/{job_id}"
    )

    assert response.status_code == 200

    fetched_job = response.json()

    assert fetched_job["id"] == job_id

    print("✅ Job retrieved")

    # ------------------------------------------------------------------
    # List jobs
    # ------------------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/api/jobs"
        f"?company_id={company_id}"
    )

    assert response.status_code == 200

    jobs = response.json()

    assert len(jobs) > 0

    print(f"✅ Listed {len(jobs)} job(s)")

    # ------------------------------------------------------------------
    # Update job
    # ------------------------------------------------------------------

    update_data = {
        "salary_min": 110000
    }

    response = requests.put(
        f"{BASE_URL}/api/jobs/{job_id}",
        json=update_data
    )

    assert response.status_code == 200
    assert response.json()["salary_min"] == 110000

    print("✅ Job updated")

    # ------------------------------------------------------------------
    # Delete/deactivate job
    # ------------------------------------------------------------------

    response = requests.delete(
        f"{BASE_URL}/api/jobs/{job_id}"
    )

    assert response.status_code == 204

    print("✅ Job deactivated")

    return job_id


# ============================================================================
# Company cleanup
# ============================================================================

def test_delete_company(company_id):
    """
    Test company soft deletion.

    The company and its Jobs should no longer
    participate in active collection.
    """

    print_section("Delete Company")

    response = requests.delete(
        f"{BASE_URL}/api/companies/{company_id}"
    )

    assert response.status_code == 204

    print("✅ Company deactivated")


# ============================================================================
# Profile cleanup
# ============================================================================

def test_delete_profile(profile_id):
    """Test deleting/deactivating a profile."""

    print_section("Delete Profile")

    response = requests.delete(
        f"{BASE_URL}/api/profiles/{profile_id}"
    )

    assert response.status_code == 204

    print("✅ Profile deactivated")


# ============================================================================
# Run all tests
# ============================================================================

def run_all_tests():
    """Run the complete integration test suite."""

    print("\n" + "=" * 60)
    print("AGENTIC JOB HUNTER API - TEST SUITE")
    print("=" * 60)

    print(f"Base URL: {BASE_URL}")

    try:

        # ------------------------------------------------------------------
        # Health
        # ------------------------------------------------------------------

        test_health_check()

        # ------------------------------------------------------------------
        # Profile
        # ------------------------------------------------------------------

        profile = test_create_profile()
        profile_id = profile["id"]

        test_get_profile(profile_id)
        test_list_profiles()
        test_update_profile(profile_id)

        # ------------------------------------------------------------------
        # CV
        # ------------------------------------------------------------------

        cv = test_create_cv(profile_id)
        cv_id = cv["id"]

        test_list_cvs(profile_id)
        test_activate_cv(cv_id)

        # ------------------------------------------------------------------
        # Preferences
        # ------------------------------------------------------------------

        test_create_preferences(profile_id)
        test_get_preferences(profile_id)
        test_update_preferences(profile_id)

        # ------------------------------------------------------------------
        # Company
        # ------------------------------------------------------------------

        company_id = test_company_endpoints()

        # ------------------------------------------------------------------
        # Jobs
        # ------------------------------------------------------------------

        test_job_endpoints(company_id)

        # ------------------------------------------------------------------
        # Cleanup
        # ------------------------------------------------------------------

        test_delete_company(company_id)

        test_delete_cv(cv_id)

        test_delete_profile(profile_id)

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:

        print(
            f"\n❌ TEST FAILED: {e}"
        )

        raise

    except requests.exceptions.ConnectionError:

        print(
            f"\n❌ Cannot connect to {BASE_URL}"
        )

        print(
            "Make sure the API is running:"
        )

        print(
            "  docker compose up api"
        )

        raise


if __name__ == "__main__":
    run_all_tests()