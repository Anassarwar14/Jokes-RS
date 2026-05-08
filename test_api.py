#!/usr/bin/env python3
"""Test script for the Jokes Recommendation API."""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    if params:
        print(f"Params: {params}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print("Unknown method")
            return None
            
        print(f"Status: {response.status_code}")
        
        try:
            body = response.json()
            print(f"Response: {json.dumps(body, indent=2)}")
            return body
        except:
            print(f"Response (text): {response.text}")
            return response
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return None

def main():
    print("Testing Jokes Recommendation API")
    print("=" * 60)
    
    # 1. Test Sessions
    print("\n### Sessions ###")
    session = test_endpoint("POST", "/api/sessions", {})
    if session:
        session_id = session.get("session_id")
        user_id = session.get("user_id")
    
    # 2. Test Jokes endpoints
    print("\n### Jokes ###")
    jokes = test_endpoint("GET", "/api/jokes", params={"limit": 5})
    
    # Get single joke
    test_endpoint("GET", "/api/jokes/0")
    test_endpoint("GET", "/api/jokes/50")
    
    # 3. Test Ratings
    print("\n### Ratings ###")
    if session:
        # Submit ratings
        for joke_id in range(0, 10):
            rating_data = {
                "session_id": session_id,
                "user_id": user_id,
                "joke_id": joke_id,
                "rating": float(5 + (joke_id % 10))
            }
            test_endpoint("POST", "/api/ratings", rating_data)
        
        # Get user ratings
        test_endpoint("GET", f"/api/ratings/{user_id}")
    
    # 4. Test Recommendations (CRITICAL - tests model loading)
    print("\n### Recommendations ###")
    if session:
        # Test PMF recommendations
        test_endpoint("GET", f"/api/recommendations/{user_id}", params={"model": "pmf", "top_k": 5})
        
        # Test Autoencoder recommendations
        test_endpoint("GET", f"/api/recommendations/{user_id}", params={"model": "autoencoder", "top_k": 5})
    
    # 5. Test Models endpoint
    print("\n### Models ###")
    test_endpoint("GET", "/api/models")
    
    print("\n" + "="*60)
    print("Testing complete!")

if __name__ == "__main__":
    main()
