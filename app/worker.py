from app.storage.base import Storage
from app.queue.base import JobQueue
from app.jobs.models import TranscodeJob
from app.transcoding.transcoder import transcode


class Worker:
    def __init__(self, queue: JobQueue, storage: Storage):
        self.queue = queue
        self.storage = storage

    def process(self, job: TranscodeJob) -> None:
        print(f"[WORKER] Processing job: {job.id}")

        input_file = self.storage.download(job.input)

        transcode(input_file=str(input_file), output_dir=job.output.path)

    def run(self) -> None:
        while True:
            job = self.queue.receive()

            if job is None:
                print("[WORKER] No more jobs.")
                break

            try:
                self.process(job)
                self.queue.complete(job)

            except Exception as error:
                self.queue.fail(job, error)
                raise
