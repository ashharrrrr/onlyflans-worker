from app.jobs.models import StorageLocation, TranscodeJob
from app.queue.local import LocalQueue
from app.storage.local import LocalStorage
from app.worker import Worker


def main():
    job = [
        TranscodeJob(
            id="test-001",
            input=StorageLocation(path="/data/input/test.mp4"),
            output=StorageLocation(
                path="/data/output/test-001",
            ),
        ),
        TranscodeJob(
            id="test-002",
            input=StorageLocation(path="/data/input/test.mp4"),
            output=StorageLocation(
                path="/data/output/test-002",
            ),
        ),
    ]
    queue = LocalQueue(job)

    storage = LocalStorage()

    worker = Worker(queue=queue, storage=storage)

    worker.run()


if __name__ == "__main__":
    main()
