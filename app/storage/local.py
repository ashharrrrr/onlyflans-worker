from pathlib import Path

from app.jobs.models import StorageLocation
from app.storage.base import Storage


class LocalStorage(Storage):
    def download(self, location: StorageLocation) -> Path:
        path = Path(location.path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return path

    def upload(self, local_path: Path, location: StorageLocation) -> None:
        destination = Path(location.path)

        destination.parent.mkdir(parents=True, exist_ok=True)

        if local_path != destination:
            destination.write_bytes(local_path.read_bytes())

        print(f"[STORAGE] Uploaded: {local_path} -> {destination}")
