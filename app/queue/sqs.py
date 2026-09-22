import json
import boto3

from app.jobs.models import TranscodeJob
from app.queue.base import JobQueue
from app.queue.s3_events import transcode_job_from_s3_event


class SQSQueue(JobQueue):
    def __init__(self, queue_url: str, region: str):
        self.queue_url = queue_url
        self.client = boto3.client("sqs", region_name=region)

        self._receipt_handles: dict[str, str] = {}

    def receive(self) -> TranscodeJob | None:
        while True:
            response = self.client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20,
                VisibilityTimeout=900,
            )

            messages = response.get("Messages", [])

            if not messages:
                return None

            message = messages[0]

            print(f"[SQS] Received message: {message['MessageId']}")
            print(f"[SQS] Body: {message['Body']}")


            job = transcode_job_from_s3_event(message["Body"])

            print(f"[SQS] Parsed job: {job}")

            if job is None:
                self.client.delete_message(
                    QueueUrl=self.queue_url, ReceiptHandle=message["ReceiptHandle"]
                )
                continue

            self._receipt_handles[job.id] = message["ReceiptHandle"]
            return job

    def complete(self, job: TranscodeJob) -> None:
        receipt_handle = self._receipt_handles.pop(job.id)

        self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )
        print(f"[SQS] Completed job: {job.id}")

    def fail(self, job: TranscodeJob, error: Exception) -> None:
        self._receipt_handles.pop(job.id, None)

        print(f"[SQS] Job Failed: {job.id}: {error}")
