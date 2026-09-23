import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

def data_root():
    return Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / "AIAudioStudio"

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    data_root:Path=data_root()
    indextts_python:Path=Path("")
    indextts_repo:Path=Path("")
    indextts_model_dir:Path=data_root()/"models"/"IndexTTS-2"
    seedvc_python:Path=Path("")
    seedvc_repo:Path=Path("")
    seedvc_model_dir:Path=data_root()/"models"/"Seed-VC"
    @property
    def uploads(self): return self.data_root/"uploads"
    @property
    def outputs(self): return self.data_root/"outputs"
settings=Settings()
settings.uploads.mkdir(parents=True,exist_ok=True)
settings.outputs.mkdir(parents=True,exist_ok=True)
