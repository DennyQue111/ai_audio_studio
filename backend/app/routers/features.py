import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from .. import services
from ..comfyui import make_audio_separation, status as comfy_status
from ..config import settings
from ..jobs import submit
from .common import save_upload

router = APIRouter()


@router.post("/api/features/song-voice-swap")
def song_voice_swap(song: UploadFile = File(...), reference: UploadFile = File(...)):
    state = comfy_status()
    if not state["online"]:
        raise HTTPException(503, "ComfyUI 未连接，请确认它运行在 " + settings.comfyui_url)
    if not state["audio_separation_ready"]:
        raise HTTPException(503, "ComfyUI 的 AudioSeparation 节点未加载，请检查节点安装状态")
    if not services.model_status()["seed_vc"]["ready"]:
        raise HTTPException(503, "Seed-VC 模型或运行环境尚未配置")
    if not settings.seedvc_python.is_file() or not settings.seedvc_repo.is_dir():
        raise HTTPException(503, "Seed-VC Python 或代码目录无效，请检查 backend/.env 中的 SEEDVC_PYTHON 和 SEEDVC_REPO")
    worker = Path(__file__).parents[1] / "workers" / "seedvc_worker.py"
    if not worker.is_file():
        raise HTTPException(503, "Seed-VC 转换 worker 文件缺失：" + str(worker))
    song_path, reference_path = save_upload(song), save_upload(reference)
    job_id = uuid.uuid4().hex
    output_dir = settings.outputs / f"song_voice_swap_{job_id}"
    output_dir.mkdir()

    def process():
        stems = make_audio_separation(song_path, f"{job_id}_separation")
        vocal_path = stems["vocals"]
        converted_dir = output_dir / "converted"
        converted_dir.mkdir()
        converted_vocals = services.convert(vocal_path, reference_path, converted_dir)
        final_song = output_dir / "song_voice_swap.wav"
        from ..audio_mix import mix_vocals_with_instrumental

        mix_vocals_with_instrumental(stems["instrumental"], converted_vocals, final_song)
        preview = output_dir / "converted_vocals.wav"
        shutil.copy2(converted_vocals, preview)
        return {"final_song": final_song, "converted_vocals": preview}

    return submit("song_voice_swap", process)
