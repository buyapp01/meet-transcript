# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Attendee is an open-source API for managing meeting bots on platforms like Zoom, Google Meet, and Microsoft Teams. It provides a REST API for joining meetings, recording audio/video, capturing transcripts, and managing bot interactions. The project is built with Django and runs as a containerized application using Docker.

## Development Setup

### Initial Setup (Windows)
```bash
# Build the Docker image (~5 minutes)
docker compose -f dev.docker-compose.yaml build

# Create local environment variables
docker compose -f dev.docker-compose.yaml run --rm attendee-app-local python init_env.py | Out-File -Encoding utf8 .env

# Edit .env and add your AWS credentials

# Start all services
docker compose -f dev.docker-compose.yaml up

# In separate terminal: Run migrations
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py migrate
```

### Initial Setup (Linux/Mac)
```bash
# Build the Docker image (~5 minutes)
docker compose -f dev.docker-compose.yaml build

# Create local environment variables
docker compose -f dev.docker-compose.yaml run --rm attendee-app-local python init_env.py > .env

# Edit .env and add your AWS credentials

# Start all services
docker compose -f dev.docker-compose.yaml up

# In separate terminal: Run migrations
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py migrate
```

### Common Commands

**Run Django server:**
```bash
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py runserver 0.0.0.0:8000
```

**Run Celery worker:**
```bash
docker compose -f dev.docker-compose.yaml exec attendee-worker-local celery -A attendee worker -l INFO
```

**Run migrations:**
```bash
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py migrate
```

**Create migrations:**
```bash
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py makemigrations
```

**Run all tests:**
```bash
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py test
```

**Run specific test file:**
```bash
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py test bots.tests.test_zoom_bot
```

**Run tests with specific tag:**
```bash
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py test --tag zoom_tests
```

**Exclude tests with specific tag:**
```bash
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py test --exclude-tag zoom_tests
```

**Lint and format code:**
```bash
ruff check --fix
ruff format
```

**Makefile shortcuts:**
```bash
make build    # Build Docker images
make up       # Start services in background
make down     # Stop services
make logs     # View logs
make migrate  # Run migrations
make lint     # Run linter and formatter
```

## Architecture Overview

### Core Components

**Bot Lifecycle:**
The system orchestrates meeting bots through several key components:
- `BotController` (bots/bot_controller/bot_controller.py) - Orchestrates the entire bot lifecycle, manages media pipelines, and coordinates between different adapters
- `BotAdapter` and platform-specific adapters (Zoom, Google Meet, Teams) - Handle platform-specific logic for joining meetings, interacting with UI elements, and managing platform features
- `BotPodCreator` (bots/bot_pod_creator/bot_pod_creator.py) - Creates Kubernetes pods or Docker containers for running bots in isolation

**Bot Adapters:**
Each meeting platform has its own adapter that extends the base `BotAdapter` class:
- `ZoomBotAdapter` - Uses the Zoom Meeting SDK (C++ bindings via Python) for native Zoom integration
- `ZoomWebBotAdapter` - Uses Selenium/Chrome for web-based Zoom meetings
- `GoogleMeetBotAdapter` - Uses Selenium/Chrome to automate Google Meet
- `TeamsBotAdapter` - Uses Selenium/Chrome to automate Microsoft Teams
- `WebBotAdapter` - Base class for all Chrome/Selenium-based adapters

**Media Pipeline:**
GStreamer-based pipeline handles audio/video processing:
- `GstreamerPipeline` - Core media processing pipeline
- `ScreenAndAudioRecorder` - Records meeting audio/video
- `AudioOutputManager` - Manages audio playback in meetings
- `VideoOutputManager` - Manages video output (bot camera)
- `PerParticipantStreamingAudioInputManager` / `PerParticipantNonStreamingAudioInputManager` - Handles per-participant audio capture
- `ClosedCaptionManager` / `GroupedClosedCaptionManager` - Manages closed captions

**API Layer:**
REST API endpoints in `bots/bots_api_views.py` provide:
- Create/manage bots (`POST /api/v1/bots`, `GET /api/v1/bots/<id>`)
- Retrieve transcripts (`GET /api/v1/bots/<id>/transcript`)
- Bot media requests (audio output, video output)
- Chat message sending
- Participant events

**Database Models:**
Core models in `bots/models.py`:
- `Bot` - Represents a bot instance with state tracking (joining, in_meeting, ended, etc.)
- `Recording` - Stores meeting recordings with transcription state
- `Utterance` - Individual speech segments from transcripts
- `Participant` - Meeting participants tracked by the bot
- `Credentials` - Encrypted platform credentials (Zoom OAuth, etc.)
- `Project` - Organizational unit for grouping bots
- `Organization` - Top-level tenant model

**Background Tasks:**
Celery tasks handle asynchronous operations:
- `run_bot_task.py` - Launches bot in container
- `sync_calendar_task.py` - Syncs calendar integrations
- `sync_zoom_oauth_connection_task.py` - Syncs Zoom OAuth connections
- Processing transcriptions, webhooks, and cleanup tasks

**Scheduler:**
Management command `run_scheduler` (bots/management/commands/run_scheduler.py) handles scheduled meetings and calendar integration.

### Key Workflows

**Joining a Meeting:**
1. API request creates `Bot` record in database
2. `launch_bot_utils.py` enqueues Celery task
3. `BotPodCreator` creates isolated container/pod
4. `run_bot` management command starts inside container
5. `BotController` instantiates appropriate `BotAdapter`
6. Adapter joins meeting using platform-specific method
7. Media pipeline starts capturing audio/video
8. Bot state updates propagate via webhooks

**Transcription Flow:**
1. Audio captured per participant via GStreamer
2. Audio chunks stored as `AudioChunk` models or streamed to transcription service
3. Deepgram (or other provider) processes audio
4. `Utterance` records created with speaker attribution
5. Webhooks fire for real-time transcript delivery
6. Full transcript available via API when meeting ends

**Calendar Integration:**
1. User connects Google/Microsoft calendar
2. Scheduler polls for upcoming meetings
3. Bots automatically created for scheduled meetings
4. Zoom OAuth connections can be mapped to specific meetings

## Settings & Configuration

Django settings split across:
- `attendee/settings/base.py` - Shared settings
- `attendee/settings/development.py` - Local development
- `attendee/settings/production.py` - Production deployment
- `attendee/settings/test.py` - Test environment

Key environment variables (see `.env`):
- `DJANGO_SETTINGS_MODULE` - Which settings file to use
- `POSTGRES_HOST` - Database host
- `REDIS_URL` - Redis connection string (for Celery)
- `CREDENTIALS_ENCRYPTION_KEY` - Fernet key for encrypting credentials
- `AWS_*` / `AZURE_*` - Cloud storage credentials

## Code Style

Ruff is used for both linting and formatting (configuration in `pyproject.toml`):
- Line length: 999 (effectively unlimited to prevent wrapping)
- Python 3.10 target
- Import sorting with `isort`
- Enabled rules: pycodestyle (E), Pyflakes (F), import sorting (I)
- Pre-commit hooks available

## Testing

Tests are organized in `bots/tests/`:
- Use Django's `TransactionTestCase` for tests that require database transactions
- Use `@tag('zoom_tests')` for tests requiring Zoom SDK
- Mock external services (Zoom API, Deepgram, etc.)
- Test database: `attendee_test` (see `.github/workflows/ci.yml`)

## API Documentation

OpenAPI schema in `docs/openapi.yml`. In development mode, access:
- Swagger UI: http://localhost:8000/schema/swagger-ui/
- ReDoc: http://localhost:8000/schema/redoc/
- Raw schema: http://localhost:8000/schema/

## Docker Services

Development compose file (`dev.docker-compose.yaml`) includes:
- `attendee-app-local` - Django web server (port 8000)
- `attendee-worker-local` - Celery worker
- `attendee-scheduler-local` - Scheduler for calendar/scheduled meetings
- `attendee-webpage-streamer-local` - Webpage streaming service (port 8001, profile: webpage-streamer)
- `postgres` - PostgreSQL 15.3
- `redis` - Redis 7

All services connect via `attendee_network` bridge network.

## Important Notes

- Chrome/Selenium bots require `seccomp` security profile (see `bots/web_bot_adapter/chrome_seccomp.json`)
- GStreamer dependencies are installed in Docker image
- Migrations are excluded from Ruff linting
- The system uses optimistic locking (`django-concurrency`) for concurrent bot updates
- Bot containers run isolated with their own Chrome/audio/video stack

---

## Recent Changes & Migration Notes

### Database Migration to Supabase (2025-10-24)

**Summary:**
Migrated from local PostgreSQL to Supabase cloud PostgreSQL database. Completed successfully with 120+ migrations creating 45 tables.

**Key Changes:**

1. **Database Configuration** ([.env](attendee/.env))
   - Changed `DATABASE_URL` to use Supabase Transaction Pooler (IPv4-compatible)
   - URL format: `postgresql://postgres.PROJECT_ID:PASSWORD@aws-1-sa-east-1.pooler.supabase.com:6543/postgres`
   - **Important:** Use Transaction Pooler (port 6543) instead of Direct Connection (port 5432) because Direct Connection is IPv6-only and may not work with all ISPs
   - Password special characters must be URL-encoded (e.g., `@` → `%40`)

2. **Storage Configuration** ([attendee/settings/base.py](attendee/attendee/settings/base.py#L221-L233))
   - Fixed Supabase storage backend configuration
   - Uses Django's `FileSystemStorage` for internal files
   - Bot recordings still use `SupabaseFileUploader` in bot_controller
   ```python
   elif STORAGE_PROTOCOL == "supabase":
       DEFAULT_STORAGE_BACKEND = {
           "BACKEND": "django.core.files.storage.FileSystemStorage",
           "OPTIONS": {
               "location": os.path.join(BASE_DIR, "media"),
               "base_url": "/media/",
           },
       }
   ```

3. **Test Settings Update** ([attendee/settings/test.py](attendee/attendee/settings/test.py))
   - Migrated from deprecated `POSTGRES_HOST` approach to modern `DATABASE_URL`
   - Uses `dj-database-url` for parsing connection strings

4. **Docker Configuration** ([dev.docker-compose.yaml](attendee/dev.docker-compose.yaml))
   - Removed IPv6 network configuration (no longer needed)
   - Simplified to basic bridge network
   - Added `.env` file loading to all services

5. **Line Endings Fix** ([entrypoint.sh](attendee/entrypoint.sh))
   - Converted from CRLF (Windows) to LF (Unix) line endings
   - Fixes `bash\r: No such file or directory` error in worker container

### Language Configuration for PT-BR Transcriptions

**Problem:** Transcriptions were coming out in English even though the meeting was in Portuguese (PT-BR).

**Root Cause:**
The system defaults to Deepgram with `language: "multi"` (auto-detection), which may detect the wrong language.

**Solution:**
Configure explicit language settings in `transcription_settings` when creating a bot:

```json
{
  "meeting_url": "https://meet.google.com/xxx-xxxx-xxx",
  "bot_name": "My Bot",
  "transcription_settings": {
    "deepgram": {
      "language": "pt"
    },
    "meeting_closed_captions": {
      "google_meet_language": "pt-BR"
    }
  }
}
```

**Available Options:**
- **Deepgram**: `language: "pt"` or `language: "pt-BR"` (see [serializers.py:254](attendee/bots/serializers.py#L254))
- **Google Meet Captions**: `google_meet_language: "pt-BR"` (explicitly supported, see [serializers.py:320-323](attendee/bots/serializers.py#L320-L323))
- **OpenAI Whisper**: `language: "pt"` (ISO 639 code)
- **AssemblyAI**: `language_code: "pt"` or use `language_detection: true`

**Documentation:** Full transcription settings schema in [bots/serializers.py:244-370](attendee/bots/serializers.py#L244-L370)

### Running Migrations Locally (Without Docker)

For cases where Docker has connectivity issues, migrations can be run directly:

**Created Script:** [run_migrations.py](attendee/run_migrations.py)
```bash
cd attendee
python run_migrations.py
```

This script:
- Loads `.env` automatically using `python-dotenv`
- Uses `--skip-checks` flag to bypass URL validation issues with Python 3.13
- Applies all pending migrations to the configured database

### Helper Scripts Created

1. **[get_api_key.py](attendee/get_api_key.py)** - Creates new API keys for testing
2. **[add_deepgram_credentials.py](attendee/add_deepgram_credentials.py)** - Adds Deepgram credentials to a project
3. **[check_transcription.py](attendee/check_transcription.py)** - Queries database to check bot transcriptions
4. **[run_migrations.py](attendee/run_migrations.py)** - Runs migrations locally without Docker

### Issues Resolved

1. **IPv6 Connectivity** ✅
   - ISP (Virtua) doesn't support IPv6
   - Solution: Use Supabase Transaction Pooler (IPv4-compatible)

2. **URL Encoding** ✅
   - Special characters in passwords must be URL-encoded
   - Example: `BuyApp@00112233` → `BuyApp%4000112233`

3. **Worker Container Startup** ✅
   - Fixed CRLF line endings in `entrypoint.sh`

4. **Python 3.13 Compatibility** ✅
   - `audioop` module removed in Python 3.13
   - Workaround: Use `--skip-checks` flag in migrations

5. **Storage Backend** ✅
   - Fixed incorrect S3Storage usage for Supabase
   - Updated to use FileSystemStorage for Django internals

### Testing Performed

**Successfully tested end-to-end bot functionality:**
- ✅ Bot creation via API
- ✅ Joining Google Meet
- ✅ Participant detection (3 participants)
- ✅ Captions enabled with pt-BR language selection
- ✅ Recording started
- ✅ Manual leave via API (`POST /bots/{id}/leave`)
- ✅ Automatic leave when alone (60s timeout)
- ✅ Transcript retrieval via API
- ✅ Post-processing state

**Bot with Portuguese transcription:**
- ✅ Created bot with `transcription_settings` for PT-BR
- ✅ Bot joined meeting with pt-BR language selected
- ⏳ Transcription testing pending (session ended)

### Environment Variables Reference

Key variables in [.env](attendee/.env):
```bash
# Database - MUST use Transaction Pooler (port 6543) for IPv4 support
DATABASE_URL=postgresql://postgres.PROJECT_ID:PASSWORD@aws-1-sa-east-1.pooler.supabase.com:6543/postgres

# Django
DJANGO_SETTINGS_MODULE=attendee.settings.development
DJANGO_SECRET_KEY=<generated>

# Storage
STORAGE_PROTOCOL=supabase
SUPABASE_URL=https://PROJECT_ID.supabase.co
SUPABASE_KEY=<anon_key>
SUPABASE_STORAGE_BUCKET=recordings

# Encryption
CREDENTIALS_ENCRYPTION_KEY=<fernet_key>

# Transcription (optional)
DEEPGRAM_API_KEY=<your_key>
```

### Next Steps / TODO

- [ ] Test Portuguese transcription with actual meeting audio
- [ ] Verify transcript language matches meeting language (PT-BR)
- [ ] Document transcription language options in API documentation
- [ ] Consider adding language parameter validation in CreateBotSerializer
- [ ] Add integration tests for different transcription providers with language settings
