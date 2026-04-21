# src/storage.py
import os

class DriveUploader:
    def __init__(self, base_url: str = os.getenv("REPORT_BASE_URL", "http://localhost:8000/reports")):
        self.base_url = base_url.rstrip("/")

    def upload(self, filename: str, content: str) -> str:
        os.makedirs("reports", exist_ok=True)
        filepath = f"reports/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"{self.base_url}/{filename}"