import subprocess
from pathlib import Path
from app.transcoding.probe import get_video_height

RESOLUTIONS = [
    {
        "name": "720p",
        "height": 720,
        "video_bitrate": "2800k",
        "audio_bitrate": "128k",
    },
    {
        "name": "480p",
        "height": 480,
        "video_bitrate": "1400k",
        "audio_bitrate": "128k",
    },
    {
        "name": "360p",
        "height": 360,
        "video_bitrate": "800k",
        "audio_bitrate": "96k",
    },
    {
        "name": "144p",
        "height": 144,
        "video_bitrate": "250k",
        "audio_bitrate": "64k",
    },
]


def get_available_resolutions(source_height: int):
    return [
        resolution
        for resolution in RESOLUTIONS
        if resolution["height"] <= source_height
    ]


def build_filter_graph(variants):
    filters = []

    split_outputs = "".join(f"[v{i}]" for i in range(len(variants)))

    filters.append(f"[0:v]split={len(variants)}{split_outputs}")

    for i, variant in enumerate(variants):
        filters.append(f"[v{i}]" f"scale=-2:{variant['height']}" f"[v{i}out]")
    return ";".join(filters)


def build_ffmpeg_command(
    input_file: str,
    output_dir: str,
    variants,
    filter_graph: str,
):
    output_path = Path(output_dir)

    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-filter_complex",
        filter_graph,
    ]

    for i, variant in enumerate(variants):
        command.extend(
            [
                "-map",
                f"[v{i}out]",
                "-map",
                "0:a?",
            ]
        )

    for i, variant in enumerate(variants):
        command.extend(
            [
                "-c:v:" + str(i),
                "libx264",
                "-b:v:" + str(i),
                variant["video_bitrate"],
                "-c:a:" + str(i),
                "aac",
                "-b:a:" + str(i),
                variant["audio_bitrate"],
            ]
        )

    command.extend(
        [
            "-preset",
            "fast",
            "-f",
            "hls",
            "-hls_time",
            "6",
            "-hls_playlist_type",
            "vod",
            "-master_pl_name",
            "master.m3u8",
            "-var_stream_map",
            " ".join(
                f"v:{i},a:{i},name:{variant['name']}"
                for i, variant in enumerate(variants)
            ),
            "-hls_segment_filename",
            str(output_path / "%v" / "segment_%03d.ts"),
            str(output_path / "%v" / "playlist.m3u8"),
        ]
    )

    return command


def run_ffmpeg(command):
    print("\nRunning FFmpeg:\n")
    print(" ".join(command))
    print()

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        print("\nFFmpeg failed.")
        raise


def transcode(input_file: str, output_dir: str):
    source_height = get_video_height(input_file)

    print(f"Source height: {source_height}p")

    variants = get_available_resolutions(source_height)

    if not variants:
        raise ValueError(f"Video is too small. Source height: {source_height}px")

    print("Generating variants:")

    for variant in variants:
        print(f"  - {variant['name']}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filter_graph = build_filter_graph(variants)

    print("\nFilter graph:")
    print(filter_graph)

    command = build_ffmpeg_command(
        input_file=input_file,
        output_dir=output_dir,
        variants=variants,
        filter_graph=filter_graph,
    )

    run_ffmpeg(command)

    print("\nTranscoding complete!")
