#!/usr/bin/env python
"""Script to add Deepgram credentials to project"""
import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv('.env')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendee.settings.development')

import django
django.setup()

from bots.models import Project, Credentials

# Get the most recent project
project = Project.objects.order_by('-created_at').first()
if not project:
    print("No projects found")
    sys.exit(1)

# Get Deepgram API key from environment
deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
if not deepgram_api_key:
    print("DEEPGRAM_API_KEY not found in .env")
    sys.exit(1)

# Check if credentials already exist
existing_creds = Credentials.objects.filter(
    project=project,
    credential_type=Credentials.CredentialTypes.DEEPGRAM
).first()

if existing_creds:
    print(f"Deepgram credentials already exist for project '{project.name}'")
else:
    # Create new credentials
    credentials = Credentials.objects.create(
        project=project,
        credential_type=Credentials.CredentialTypes.DEEPGRAM
    )
    credentials.set_credentials({"api_key": deepgram_api_key})
    print(f"Deepgram credentials added to project '{project.name}'")
