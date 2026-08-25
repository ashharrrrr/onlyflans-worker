import json
import boto3

from app.jobs.models import TranscodeJob
from app.queue.base import JobQueue


class SQSQueue(JobQueue):
    def __init__(self, queue_url: str, region: str):
        self.queue_url = queue_url
        self.client = boto3.client("sqs", region_name=region)

        self._receipt_handles: dict[str, str] = {}

    def receive(self) -> TranscodeJob | None:
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
            VisibilityTimeout=30,
        )

        messages = response.get("Messages", [])

        if not messages:
            return None

        message = messages[0]

        body = json.loads(message["Body"])

        job = TranscodeJob.model_validate(body)

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
