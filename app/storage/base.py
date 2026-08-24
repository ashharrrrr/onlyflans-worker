from abc import ABC, abstractmethod
from pathlib import Path


from app.jobs.models import StorageLocation


class Storage(ABC):
    @abstractmethod
    def download(self, location: StorageLocation) -> Path:
        pass

    @abstractmethod
    def upload(self, local_path: Path, location: StorageLocation) -> None:
        pass
