"""
Simple test script to verify the API is working
"""
import sys
import time

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health check passed")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Root endpoint passed - {data['message']}")
            return True
        else:
            print(f"✗ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
        return False

def test_status():
    """Test status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status endpoint passed")
            print(f"  - Model loaded: {data.get('model_loaded')}")
            print(f"  - Data loaded: {data.get('data_loaded')}")
            return True
        else:
            print(f"✗ Status endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Status endpoint failed: {e}")
        return False

def main():
    print("Testing Stock Prediction API...\n")

    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            break
        except:
            time.sleep(2)
            print(f"  Attempt {i+1}/10...")
    else:
        print("✗ Server did not start in time")
        sys.exit(1)

    print()

    # Run tests
    results = []
    results.append(test_health())
    results.append(test_root())
    results.append(test_status())

    print()
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
