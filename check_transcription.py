#!/usr/bin/env python
"""Script to check bot transcriptions"""
import os
from dotenv import load_dotenv

# Load .env
load_dotenv('.env')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendee.settings.development')

import django
django.setup()

from bots.models import Bot, Utterance, Recording

# Get the bot
bot_id = "bot_LbL4D4tKswQRfEhH"
try:
    bot = Bot.objects.get(object_id=bot_id)
    print(f"Bot: {bot.object_id}")
    print(f"State: {bot.state}")
    print(f"Meeting URL: {bot.meeting_url}")

    # Get recording
    recording = Recording.objects.filter(bot=bot, is_default_recording=True).first()
    if recording:
        print(f"\nRecording found: {recording.object_id}")

        # Get utterances with transcriptions
        utterances = Utterance.objects.filter(
            recording=recording,
            transcription__isnull=False
        ).order_by('timestamp_ms')[:5]  # First 5

        print(f"Total utterances with transcription: {utterances.count()}")

        for i, utt in enumerate(utterances, 1):
            transcript_text = utt.transcription.get('transcript', '')
            print(f"\n{i}. Speaker: {utt.participant.full_name if utt.participant else 'Unknown'}")
            print(f"   Text: {transcript_text}")
    else:
        print("\nNo recording found")

except Bot.DoesNotExist:
    print(f"Bot {bot_id} not found")
except Exception as e:
    print(f"Error: {e}")
