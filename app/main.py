from app.jobs.models import StorageLocation, TranscodeJob
from app.queue.local import LocalQueue
from app.storage.local import LocalStorage
from app.transcoding.transcoder import transcode


def main():
    job = TranscodeJob(
        id="test-001",
        input=StorageLocation(path="input/test.mp4"),
        output=StorageLocation(
            path="output/test-001",
        ),
    )

    queue = LocalQueue([job])

    storage = LocalStorage()

    while True:
        job = queue.receive()

        if job is None:
            print("[WORKER] No more jobs.")
            break

        print(f"[WOKER] Processing job: {job.id}")

        try:
            input_file = storage.download(job.input)

            transcode(input_file=str(input_file), output_dir=job.output.path)

            queue.complete(job)

        except Exception as error:
            queue.fail(job, error)
            raise


if __name__ == "__main__":
    main()
