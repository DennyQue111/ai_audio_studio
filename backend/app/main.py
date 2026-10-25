import shutil,threading,uuid
from pathlib import Path
import mimetypes
from fastapi import FastAPI,File,Form,HTTPException,UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .config import settings
from .services import model_status,tts,convert
from .comfyui import (
    STABLE_AUDIO_MAX_SECONDS,
    make_audio_separation,
    make_stable_audio,
    make_voice_design,
    status as comfy_status,
)
app=FastAPI(title="AI Audio Studio")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5178",
        "http://127.0.0.1:5178",
        "http://localhost:5179",
        "http://127.0.0.1:5179",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
jobs={}
def save(f):
    ext=Path(f.filename or ".wav").suffix.lower()
    if ext not in {".wav",".mp3",".flac",".m4a",".ogg"}: raise HTTPException(400,"不支持的音频格式")
    p=settings.uploads/(uuid.uuid4().hex+ext)
    with p.open("wb") as o: shutil.copyfileobj(f.file,o)
    return p
def submit(kind,fn):
    i=uuid.uuid4().hex;jobs[i]={"id":i,"kind":kind,"status":"queued","message":"等待执行"}
    def work():
        jobs[i].update(status="running",message="模型处理中")
        try:
            out=fn()
            if isinstance(out, dict):
                output_files=[{"name":name,"path":str(path)} for name,path in out.items()]
                outputs=[{"name":item["name"],"download":f"/api/jobs/{i}/outputs/{index}/download"} for index,item in enumerate(output_files)]
                jobs[i].update(status="completed",message="处理完成",outputs=outputs,_output_files=output_files)
            else:
                jobs[i].update(status="completed",message="处理完成",output=str(out),download="/api/jobs/"+i+"/download")
        except Exception as e: jobs[i].update(status="failed",message="处理失败",error=str(e))
    threading.Thread(target=work,daemon=True).start();return {"job_id":i}
@app.get("/api/models")
def models():
    state = model_status()
    state["comfyui"] = comfy_status()
    return state
@app.post("/api/tts")
def make_tts(text:str=Form(...),emotion_text:str=Form(""),voice:UploadFile=File(...)):
    if not model_status()["indextts2"]["ready"]: raise HTTPException(503,"IndexTTS2尚未配置")
    v=save(voice);o=settings.outputs/("tts_"+uuid.uuid4().hex+".wav")
    return submit("tts",lambda:tts(text,v,o,emotion_text))
@app.post("/api/voice-conversion")
def vc(source:UploadFile=File(...),reference:UploadFile=File(...)):
    if not model_status()["seed_vc"]["ready"]: raise HTTPException(503,"Seed-VC尚未配置")
    s,r=save(source),save(reference);d=settings.outputs/("vc_"+uuid.uuid4().hex);d.mkdir()
    return submit("voice_conversion",lambda:convert(s,r,d))
@app.post("/api/generate/voice-design")
def generate_voice_design(text:str=Form(...,min_length=1,max_length=12000),voice_description:str=Form(...,min_length=1,max_length=6000)):
    state=comfy_status()
    if not state["online"]: raise HTTPException(503,"ComfyUI 未连接，请确认它运行在 "+settings.comfyui_url)
    if not state["qwen_voice_design_ready"]:
        missing="、".join(state["qwen_voice_design_missing"])
        raise HTTPException(503,"Qwen3-TTS VoiceDesign 尚未就绪，缺少："+missing)
    job_id=uuid.uuid4().hex
    return submit("voice_design",lambda:make_voice_design(text,voice_description,job_id))


def _submit_stable_audio(prompt: str, category: str, duration: int):
    if category not in {"music","sfx"}: raise HTTPException(400,"category 只能是 music 或 sfx")
    state=comfy_status()
    if not state["online"]: raise HTTPException(503,"ComfyUI 未连接，请确认它运行在 "+settings.comfyui_url)
    ready_key="stable_audio_music_ready" if category=="music" else "stable_audio_sfx_ready"
    if not state[ready_key]:
        missing_key="stable_audio_music_missing" if category=="music" else "stable_audio_sfx_missing"
        missing="、".join(state[missing_key])
        raise HTTPException(503,"Stable Audio 3 模型未就绪，缺少文件："+missing)
    job_id=uuid.uuid4().hex
    return submit("stable_audio_"+category,lambda:make_stable_audio(prompt,category,duration,job_id))


@app.post("/api/generate/music")
def generate_music(
    prompt: str = Form(..., min_length=1, max_length=4000),
    duration: int = Form(15, ge=1, le=STABLE_AUDIO_MAX_SECONDS),
):
    return _submit_stable_audio(prompt, "music", duration)


@app.post("/api/generate/sfx")
def generate_sfx(
    prompt: str = Form(..., min_length=1, max_length=4000),
    duration: int = Form(15, ge=1, le=STABLE_AUDIO_MAX_SECONDS),
):
    return _submit_stable_audio(prompt, "sfx", duration)


@app.post("/api/audio-separation")
def audio_separation(audio: UploadFile = File(...)):
    state = comfy_status()
    if not state["online"]:
        raise HTTPException(503,"ComfyUI 未连接，请确认它运行在 "+settings.comfyui_url)
    if not state["audio_separation_ready"]:
        raise HTTPException(503,"ComfyUI 的 AudioSeparation 节点未加载，请检查节点安装状态")
    if audio.size and audio.size > 250 * 1024 * 1024:
        raise HTTPException(413,"音频文件不能超过 250 MB")
    source = save(audio)
    job_id = uuid.uuid4().hex
    return submit("audio_separation",lambda:make_audio_separation(source,job_id))


@app.post("/api/generate/stable-audio")
def generate_stable_audio(
    prompt: str = Form(..., min_length=1, max_length=4000),
    category: str = Form("music"),
    duration: int = Form(15, ge=1, le=STABLE_AUDIO_MAX_SECONDS),
):
    """Backward-compatible endpoint for clients that still select a category."""
    return _submit_stable_audio(prompt, category, duration)
@app.get("/api/jobs/{i}")
def job(i:str):
    if i not in jobs: raise HTTPException(404,"任务不存在")
    return {key:value for key,value in jobs[i].items() if not key.startswith("_")}


@app.get("/api/jobs/{i}/outputs/{index}/download")
def download_output(i: str, index: int):
    output_files = jobs.get(i, {}).get("_output_files", [])
    if index < 0 or index >= len(output_files): raise HTTPException(404,"结果不存在")
    p = Path(output_files[index]["path"])
    if not p.is_file(): raise HTTPException(404,"结果不存在")
    return FileResponse(p,filename=p.name,media_type=mimetypes.guess_type(p.name)[0] or "application/octet-stream")
@app.get("/api/jobs/{i}/download")
def download(i:str):
    p=Path(jobs.get(i,{}).get("output",""))
    if not p.is_file(): raise HTTPException(404,"结果不存在")
    return FileResponse(p,filename=p.name,media_type=mimetypes.guess_type(p.name)[0] or "application/octet-stream")
