#!/usr/bin/env python3
"""Test ClickUp authentication"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

token = os.getenv('CLICKUP_API_TOKEN')
print(f"Token loaded: {repr(token)}")
print(f"Token length: {len(token) if token else 0}")
print(f"Token first 20 chars: {token[:20] if token else 'NONE'}...")

# Test user endpoint
headers = {
    'Authorization': token,
    'Content-Type': 'application/json'
}

print("\n=== Testing /user endpoint ===")
resp = requests.get('https://api.clickup.com/api/v2/user', headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:200]}")

# Test list endpoint
list_id = "901605696286"
user_id = "81756915"
url = f"https://api.clickup.com/api/v2/list/{list_id}/task?assignees%5B%5D={user_id}&include_closed=true&subtasks=true"

print(f"\n=== Testing /list/{list_id}/task endpoint ===")
resp2 = requests.get(url, headers=headers)
print(f"Status: {resp2.status_code}")
print(f"Response: {resp2.text[:200]}")
