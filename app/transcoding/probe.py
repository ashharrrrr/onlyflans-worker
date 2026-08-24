import subprocess
import json


def get_video_height(input_file: str) -> int:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=height",
        "-of",
        "json",
        input_file,
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        print("ffprobe failed:")
        print(e.stderr)
        raise

    data = json.loads(result.stdout)

    return data["streams"][0]["height"]
