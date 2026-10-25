import uuid

from fastapi import APIRouter, Form, HTTPException

from ..comfyui import STABLE_AUDIO_MAX_SECONDS, make_stable_audio, status as comfy_status
from ..config import settings
from ..jobs import submit

router = APIRouter()


def submit_stable_audio(prompt: str, category: str, duration: int):
    state = comfy_status()
    if not state["online"]:
        raise HTTPException(503, "ComfyUI 未连接，请确认它运行在 " + settings.comfyui_url)
    ready_key = f"stable_audio_{category}_ready"
    if not state[ready_key]:
        missing_key = f"stable_audio_{category}_missing"
        raise HTTPException(503, "Stable Audio 3 模型未就绪，缺少文件：" + "、".join(state[missing_key]))
    job_id = uuid.uuid4().hex
    return submit(f"stable_audio_{category}", lambda: make_stable_audio(prompt, category, duration, job_id))


@router.post("/api/generate/music")
def generate_music(prompt: str = Form(..., min_length=1, max_length=4000), duration: int = Form(15, ge=1, le=STABLE_AUDIO_MAX_SECONDS)):
    return submit_stable_audio(prompt, "music", duration)


@router.post("/api/generate/sfx")
def generate_sfx(prompt: str = Form(..., min_length=1, max_length=4000), duration: int = Form(15, ge=1, le=STABLE_AUDIO_MAX_SECONDS)):
    return submit_stable_audio(prompt, "sfx", duration)


@router.post("/api/generate/stable-audio")
def generate_stable_audio(
    prompt: str = Form(..., min_length=1, max_length=4000),
    category: str = Form("music"),
    duration: int = Form(15, ge=1, le=STABLE_AUDIO_MAX_SECONDS),
):
    if category not in {"music", "sfx"}:
        raise HTTPException(400, "category 只能是 music 或 sfx")
    return submit_stable_audio(prompt, category, duration)
