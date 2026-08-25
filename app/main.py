from app.jobs.models import StorageLocation, TranscodeJob
from app.worker import Worker
from app.config import settings
from app.factory import create_storage, create_queue


def main():
    print("storage backend:", settings.storage_backend)
    print("s3 bucket:", settings.s3_bucket)
    job = [
        TranscodeJob(
            id="test-s3-001",
            input=StorageLocation(
                uri="s3://onlyflans-media-videos/uploads/test-s3-001/test.mp4"
            ),
            output=StorageLocation(
                uri="s3://onlyflans-media-videos/videos/test-s3-001/",
            ),
        ),
    ]
    queue = create_queue(job)

    storage = create_storage()

    worker = Worker(queue=queue, storage=storage)

    worker.run()


if __name__ == "__main__":
    main()
