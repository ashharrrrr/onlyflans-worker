import json
from urllib.parse import unquote_plus

from app.jobs.models import StorageLocation, TranscodeJob


def transcode_job_from_s3_event(body: str) -> TranscodeJob | None:
    event = json.loads(body)

    if event.get("Event") == "s3:TestEvent":
        return None

    record = event["Records"][0]

    bucket = record["s3"]["bucket"]["name"]
    key = unquote_plus(record["s3"]["object"]["key"])

    parts = key.split("/")

    if len(parts) != 6:
        raise ValueError(f"Unexpected S3 key: {key}")

    if (
        parts[0] != "users"
        or parts[2] != "videos"
        or parts[4] != "original"
        or parts[5] != "source.mp4"
    ):
        raise ValueError(f"Unexpected S3 key: {key}")

    user_id = parts[1]
    video_id = parts[3]

    output_key = f"users/{user_id}/videos/{video_id}/hls/"

    return TranscodeJob(
        id=video_id,
        input=StorageLocation(
            uri=f"s3://{bucket}/{key}",
        ),
        output=StorageLocation(
            uri=f"s3://{bucket}/{output_key}",
        ),
    )
