#!/usr/bin/env python
"""Script para rodar migrations carregando .env"""
import os
import sys
from dotenv import load_dotenv

# Carregar .env
load_dotenv('.env')

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendee.settings.development')

# Rodar migrations com --skip-checks para evitar problemas com Python 3.13
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate', '--skip-checks'])
