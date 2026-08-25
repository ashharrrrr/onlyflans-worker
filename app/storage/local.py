from pathlib import Path

from app.jobs.models import StorageLocation
from app.storage.base import Storage


class LocalStorage(Storage):
    def download(self, location: StorageLocation) -> Path:
        path = Path(location.uri)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return path

    def upload(self, local_path: Path, location: StorageLocation) -> None:
        destination = Path(location.uri)

        destination.parent.mkdir(parents=True, exist_ok=True)

        if local_path != destination:
            destination.write_bytes(local_path.read_bytes())

        print(f"[STORAGE] Uploaded: {local_path} -> {destination}")

    def upload_directory(
        self,
        local_dir: Path,
        location: StorageLocation,
    ) -> None:
        destination = Path(location.uri)

        for file in local_dir.rglob("*"):
            if not file.is_file():
                continue

            relative_path = file.relative_to(local_dir)
            target = destination / relative_path

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(file.read_bytes())

            print(f"[STORAGE] Uploaded: {file} -> {target}")
