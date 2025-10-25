@echo off
set DJANGO_SETTINGS_MODULE=attendee.settings.development
set DATABASE_URL=postgresql://postgres:BuyApp%%4000112233@db.xldcnftfwebpaytstrbi.supabase.co:5432/postgres
set CREDENTIALS_ENCRYPTION_KEY=vCJHbsQKy0su_c3Wd6Ye2gCEHrpEzp82UBctCGaRgLg=
set DJANGO_SECRET_KEY=0+(qne41sra%%!9s^=v^&^&zo_f(pz-as2#nzen^3z4iv!bkvb%%4c
set STORAGE_PROTOCOL=supabase
set SUPABASE_URL=https://xldcnftfwebpaytstrbi.supabase.co
set SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZGNuZnRmd2VicGF5dHN0cmJpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMyODIwNSwiZXhwIjoyMDc2OTA0MjA1fQ.oNHeGDBpuWeMB17p5YXx5igD16WEx57hEzu0Ot6oip0
set SUPABASE_BUCKET_NAME=meeting-recordings

python manage.py migrate
