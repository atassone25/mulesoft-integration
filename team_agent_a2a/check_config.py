#!/usr/bin/env python3
"""Quick config check for Data AI Agent"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("Data AI Agent Configuration Check")
print("=" * 60)

# Load parent .env
parent_dir = Path(__file__).parent.parent
env_file = parent_dir / '.env'

if env_file.exists():
    print(f"✅ Found .env at: {env_file}")
    load_dotenv(env_file)
else:
    print(f"❌ .env not found at: {env_file}")
    sys.exit(1)

# Check key variables
project = os.getenv('GOOGLE_CLOUD_PROJECT')
location = os.getenv('GOOGLE_CLOUD_LOCATION')
engine_id = os.getenv('AGENT_ENGINE_ID')
use_vertexai = os.getenv('GOOGLE_GENAI_USE_VERTEXAI')

print(f"\n📊 Environment Variables:")
print(f"  GOOGLE_CLOUD_PROJECT: {project}")
print(f"  GOOGLE_CLOUD_LOCATION: {location}")
print(f"  AGENT_ENGINE_ID: {engine_id}")
print(f"  GOOGLE_GENAI_USE_VERTEXAI: {use_vertexai}")

# Validate
print(f"\n🔍 Validation:")
if project:
    print(f"  ✅ Project ID set")
else:
    print(f"  ❌ Project ID missing")

if location:
    print(f"  ✅ Location set")
else:
    print(f"  ❌ Location missing")

if engine_id:
    print(f"  ✅ Engine ID set")
    if engine_id == "4388410391198171136":
        print(f"     ✅ Correct engine ID!")
    else:
        print(f"     ⚠️  Unexpected engine ID: {engine_id}")
else:
    print(f"  ❌ Engine ID missing")

if use_vertexai and use_vertexai.upper() in ['TRUE', '1', 'YES']:
    print(f"  ✅ Vertex AI enabled")
else:
    print(f"  ⚠️  Vertex AI not explicitly enabled")

print("\n" + "=" * 60)
print("Configuration check complete!")
print("=" * 60)
