from app.jobs.models import TranscodeJob
from app.queue.base import JobQueue


class LocalQueue(JobQueue):
    def __init__(self, jobs: list[TranscodeJob]):
        self.jobs = jobs

    def receive(self) -> TranscodeJob | None:
        if not self.jobs:
            return None

        return self.jobs.pop(0)

    def complete(self, job: TranscodeJob) -> None:
        print(f"[QUEUE] Job complete: {job.id}")

    def fail(self, job: TranscodeJob, error: Exception) -> None:
        print(f"[QUEUE] Job failed: {job.id}: {error}")
