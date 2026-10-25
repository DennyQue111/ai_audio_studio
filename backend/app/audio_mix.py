import shutil
import subprocess
from pathlib import Path


def _probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def mix_vocals_with_instrumental(instrumental: Path, vocals: Path, output: Path) -> Path:
    """Mix aligned stems; add silence to the shorter track and preserve full song duration."""
    duration = max(_probe_duration(instrumental), _probe_duration(vocals))
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("找不到 FFmpeg，请确认 ffmpeg 已添加到 PATH")
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(instrumental),
        "-i",
        str(vocals),
        "-filter_complex",
        f"[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[bg];"
        f"[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[vox];"
        f"[bg][vox]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.98,"
        f"atrim=duration={duration:.6f}[out]",
        "-map",
        "[out]",
        "-c:a",
        "pcm_s16le",
        str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "合成歌曲失败")[-4000:])
    return output
