import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .. import services
from ..comfyui import make_voice_design, status as comfy_status
from ..config import settings
from ..jobs import submit
from .common import save_upload

router = APIRouter()


@router.post("/api/tts")
def make_tts(text: str = Form(...), emotion_text: str = Form(""), voice: UploadFile = File(...)):
    if not services.model_status()["indextts2"]["ready"]:
        raise HTTPException(503, "IndexTTS2尚未配置")
    voice_path = save_upload(voice)
    output = settings.outputs / f"tts_{uuid.uuid4().hex}.wav"
    return submit("tts", lambda: services.tts(text, voice_path, output, emotion_text))


@router.post("/api/voice-conversion")
def voice_conversion(source: UploadFile = File(...), reference: UploadFile = File(...)):
    if not services.model_status()["seed_vc"]["ready"]:
        raise HTTPException(503, "Seed-VC尚未配置")
    source_path, reference_path = save_upload(source), save_upload(reference)
    output_dir = settings.outputs / f"vc_{uuid.uuid4().hex}"
    output_dir.mkdir()
    return submit("voice_conversion", lambda: services.convert(source_path, reference_path, output_dir))


@router.post("/api/generate/voice-design")
def generate_voice_design(
    text: str = Form(..., min_length=1, max_length=12000),
    voice_description: str = Form(..., min_length=1, max_length=6000),
):
    state = comfy_status()
    if not state["online"]:
        raise HTTPException(503, "ComfyUI 未连接，请确认它运行在 " + settings.comfyui_url)
    if not state["qwen_voice_design_ready"]:
        raise HTTPException(503, "Qwen3-TTS VoiceDesign 尚未就绪，缺少：" + "、".join(state["qwen_voice_design_missing"]))
    job_id = uuid.uuid4().hex
    return submit("voice_design", lambda: make_voice_design(text, voice_description, job_id))
