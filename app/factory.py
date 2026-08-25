from app.config import settings
from app.queue.base import JobQueue
from app.queue.local import LocalQueue
from app.storage.base import Storage
from app.storage.local import LocalStorage
from app.storage.s3 import S3Storage
from app.queue.sqs import SQSQueue


def create_queue(jobs) -> JobQueue:
    if settings.queue_backend == "local":
        return LocalQueue(jobs)

    if settings.queue_backend == "sqs":
        return SQSQueue(queue_url=settings.sqs_queue_url, region=settings.aws_region)

    raise ValueError(f"Unsupported queue backend: {settings.queue_backend}")


def create_storage() -> Storage:
    if settings.storage_backend == "local":
        return LocalStorage()

    if settings.storage_backend == "s3":
        return S3Storage(
            bucket=settings.s3_bucket,
            region=settings.aws_region,
        )

    raise ValueError(f"Unsupported storage backend: {settings.storage_backend}")
