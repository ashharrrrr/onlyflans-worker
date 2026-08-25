from pathlib import Path
from urllib.parse import urlparse

import boto3

from app.jobs.models import StorageLocation
from app.storage.base import Storage


class S3Storage(Storage):
    def __init__(self, bucket: str, region: str):
        self.bucket = bucket
        self.client = boto3.client("s3", region_name=region)

    def _key(self, location: StorageLocation) -> str:
        parsed = urlparse(location.uri)

        if parsed.scheme != "s3":
            raise ValueError(f"Excepted S3 URI, got: {location.uri}")

        if parsed.netloc != self.bucket:
            raise ValueError(f"Expected bucket {self.bucket}, " f"got {parsed.netloc}")

        return parsed.path.lstrip("/")

    def download(self, location: StorageLocation, destination: Path) -> Path:
        key = self._key(location)

        destination.mkdir(parents=True, exist_ok=True)
        filename = destination / Path(key).name

        print(f"[S3] Downloading s3://{self.bucket}/{key}")

        self.client.download_file(self.bucket, key, str(filename))

        return filename

    def _get_content_type(self, path: Path) -> str:
        content_types = {".m3u8": "application/vnd.apple.mpegurl", ".ts": "video/mp2t"}
        return content_types.get(path.suffix.lower(), "application/octet-stream")

    def upload(self, local_path: Path, location: StorageLocation) -> None:
        key = self._key(location)

        print(f"[S3] Uploading {local_path} -> s3://{self.bucket}/{key}")

        self.client.upload_file(str(local_path), self.bucket, key, ExtraArgs={"ContentType": self._get_content_type(local_path)})

    def upload_directory(self, local_dir: Path, location: StorageLocation) -> None:
        prefix = self._key(location).rstrip("/")

        for file in local_dir.rglob("*"):
            if not file.is_file():
                continue

            relative_path = file.relative_to(local_dir)
            key = f"{prefix}/{relative_path}"

            print(f"[S3] Uploading {file} -> s3://{self.bucket}/{key}")

            self.client.upload_file(str(file), self.bucket, key, ExtraArgs={"ContentType": self._get_content_type(file)})
