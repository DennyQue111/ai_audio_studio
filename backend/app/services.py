import subprocess,sys
from pathlib import Path
from .config import settings

INDEX_FILES=("config.yaml","bpe.model","gpt.pth","s2mel.pth")
SEED_FILES=("v2/ar_base.pth","v2/cfm_small.pth")

def model_status():
    def item(python,repo,models,files):
        missing=[x for x in files if not (models/x).exists()]
        return {"ready":python.is_file() and repo.is_dir() and not missing,"models":str(models),"missing":missing}
    return {"indextts2":item(settings.indextts_python,settings.indextts_repo,settings.indextts_model_dir,INDEX_FILES),
            "seed_vc":item(settings.seedvc_python,settings.seedvc_repo,settings.seedvc_model_dir,SEED_FILES)}

def run(cmd,cwd):
    p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,encoding="utf-8",errors="replace",creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    if p.returncode: raise RuntimeError((p.stderr or p.stdout or "模型运行失败")[-4000:])

def tts(text,voice,output,emotion=""):
    worker=Path(__file__).parents[1]/"workers"/"indextts_worker.py"
    cmd=[str(settings.indextts_python),str(worker),"--repo",str(settings.indextts_repo),"--models",str(settings.indextts_model_dir),"--text",text,"--voice",str(voice),"--output",str(output)]
    if emotion: cmd+=["--emotion",emotion]
    run(cmd,settings.indextts_repo)
    return output

def convert(source,reference,outdir):
    cmd=[str(settings.seedvc_python),str(settings.seedvc_repo/"inference_v2.py"),"--source",str(source),"--target",str(reference),"--output",str(outdir),"--diffusion-steps","25","--intelligibility-cfg-rate","0.7","--similarity-cfg-rate","0.7","--convert-style","true","--cfm-checkpoint-path",str(settings.seedvc_model_dir/"v2"/"cfm_small.pth"),"--ar-checkpoint-path",str(settings.seedvc_model_dir/"v2"/"ar_base.pth")]
    run(cmd,settings.seedvc_repo)
    wavs=sorted(outdir.glob("*.wav"),key=lambda p:p.stat().st_mtime,reverse=True)
    if not wavs: raise RuntimeError("Seed-VC没有生成WAV")
    return wavs[0]
