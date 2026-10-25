import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..comfyui import make_audio_separation, status as comfy_status
from ..config import settings
from ..jobs import submit
from .common import save_upload

router = APIRouter()


@router.post("/api/audio-separation")
def audio_separation(audio: UploadFile = File(...)):
    state = comfy_status()
    if not state["online"]:
        raise HTTPException(503, "ComfyUI 未连接，请确认它运行在 " + settings.comfyui_url)
    if not state["audio_separation_ready"]:
        raise HTTPException(503, "ComfyUI 的 AudioSeparation 节点未加载，请检查节点安装状态")
    source = save_upload(audio)
    job_id = uuid.uuid4().hex
    return submit("audio_separation", lambda: make_audio_separation(source, job_id))
