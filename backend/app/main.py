import shutil,threading,uuid
from pathlib import Path
from fastapi import FastAPI,File,Form,HTTPException,UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .config import settings
from .services import model_status,tts,convert
app=FastAPI(title="AI Audio Studio")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173"],allow_methods=["*"],allow_headers=["*"])
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
            out=fn();jobs[i].update(status="completed",message="处理完成",output=str(out),download="/api/jobs/"+i+"/download")
        except Exception as e: jobs[i].update(status="failed",message="处理失败",error=str(e))
    threading.Thread(target=work,daemon=True).start();return {"job_id":i}
@app.get("/api/models")
def models(): return model_status()
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
@app.get("/api/jobs/{i}")
def job(i:str):
    if i not in jobs: raise HTTPException(404,"任务不存在")
    return jobs[i]
@app.get("/api/jobs/{i}/download")
def download(i:str):
    p=Path(jobs.get(i,{}).get("output",""))
    if not p.is_file(): raise HTTPException(404,"结果不存在")
    return FileResponse(p,filename=p.name,media_type="audio/wav")
