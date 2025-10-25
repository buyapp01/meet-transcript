import logging
import threading
from pathlib import Path

from supabase import create_client, Client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SupabaseFileUploader:
    def __init__(self, bucket, filename, supabase_url=None, supabase_key=None):
        """Initialize the SupabaseFileUploader with a Supabase bucket name.

        Args:
            bucket (str): The name of the Supabase bucket to upload to
            filename (str): The name of the to be stored file
            supabase_url (str): The Supabase project URL
            supabase_key (str): The Supabase service role key
        """
        if not supabase_url or not supabase_key:
            raise ValueError("supabase_url and supabase_key are required")

        self.supabase_client: Client = create_client(supabase_url, supabase_key)
        self.bucket = bucket
        self.filename = filename
        self._upload_thread = None

    def upload_file(self, file_path: str, callback=None):
        """Start an asynchronous upload of a file to Supabase Storage.

        Args:
            file_path (str): Path to the local file to upload
            callback (callable, optional): Function to call when upload completes
        """
        self._upload_thread = threading.Thread(target=self._upload_worker, args=(file_path, callback), daemon=True)
        self._upload_thread.start()

    def _upload_worker(self, file_path: str, callback=None):
        """Background thread that handles the actual file upload.

        Args:
            file_path (str): Path to the local file to upload
            callback (callable, optional): Function to call when upload completes
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read the file and upload to Supabase Storage
            with open(file_path, "rb") as f:
                file_data = f.read()

            response = self.supabase_client.storage.from_(self.bucket).upload(
                path=self.filename,
                file=file_data,
                file_options={"content-type": "application/octet-stream"}
            )

            logger.info(f"Successfully uploaded {file_path} to supabase://{self.bucket}/{self.filename}")

            if callback:
                callback(True)

        except Exception as e:
            logger.error(f"Upload error: {e}")
            if callback:
                callback(False)

    def wait_for_upload(self):
        """Wait for the current upload to complete."""
        if self._upload_thread and self._upload_thread.is_alive():
            self._upload_thread.join()

    def delete_file(self, file_path: str):
        """Delete a file from the local filesystem."""
        file_path = Path(file_path)
        if file_path.exists():
            file_path.unlink()
