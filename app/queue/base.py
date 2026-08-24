from abc import ABC, abstractmethod

from app.jobs.models import TranscodeJob


class JobQueue(ABC):
    @abstractmethod
    def receive(self) -> TranscodeJob | None:
        pass

    @abstractmethod
    def complete(self, job: TranscodeJob) -> None:
        pass

    @abstractmethod
    def fail(self, job: TranscodeJob, error: Exception) -> None:
        pass
