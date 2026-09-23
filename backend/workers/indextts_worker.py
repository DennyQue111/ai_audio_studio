import argparse,sys
from pathlib import Path
p=argparse.ArgumentParser()
for n in ("repo","models","text","voice","output"): p.add_argument("--"+n,required=True)
p.add_argument("--emotion",default="")
a=p.parse_args();sys.path.insert(0,a.repo)
from indextts.infer_v2 import IndexTTS2
m=IndexTTS2(cfg_path=str(Path(a.models)/"config.yaml"),model_dir=a.models,use_fp16=True,device="cuda:0",use_cuda_kernel=False,use_deepspeed=False,use_qwen_emo=bool(a.emotion))
kw={"spk_audio_prompt":a.voice,"text":a.text,"output_path":a.output,"verbose":True}
if a.emotion: kw.update(use_emo_text=True,emo_text=a.emotion,emo_alpha=.8)
m.infer(**kw)
