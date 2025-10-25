#!/usr/bin/env python
"""Script to retrieve API key"""
import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv('.env')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendee.settings.development')

import django
django.setup()

from bots.models import ApiKey, Project

# Get the most recent project
project = Project.objects.order_by('-created_at').first()
if not project:
    print("No projects found. Please create a project first.")
    sys.exit(1)

# Create a new API key
api_key_obj, api_key_plain = ApiKey.create(project=project, name="PT-BR Test Key")
print(f"New API Key created: {api_key_plain}")
print(f"Project: {project.name}")
print(f"Organization: {project.organization.name}")
