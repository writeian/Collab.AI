#!/usr/bin/env python3
"""Test script to verify .env file is loaded correctly."""

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Test if variables are loaded
api_key = os.getenv("OPENAI_API_KEY")
secret_key = os.getenv("SECRET_KEY")

print("Environment Variables Test:")
print("-" * 30)
print(f"OPENAI_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
print(f"SECRET_KEY: {'✅ Set' if secret_key else '❌ Not set'}")

if api_key:
    print(f"API Key starts with: {api_key[:10]}...")
else:
    print("❌ Please add OPENAI_API_KEY to your .env file")

if secret_key:
    print(f"Secret key length: {len(secret_key)} characters")
else:
    print("❌ Please add SECRET_KEY to your .env file") 