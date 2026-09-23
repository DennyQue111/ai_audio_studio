import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

def default_data_root() -> Path:
    return Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / "AIAudioStudio"

_DEFAULT_DATA_ROOT = default_data_root()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    data_root: Path = _DEFAULT_DATA_ROOT
    indextts_python: Path = Path("")
    indextts_repo: Path = Path("")
    indextts_model_dir: Path = _DEFAULT_DATA_ROOT / "models" / "IndexTTS-2"
    seedvc_python: Path = Path("")
    seedvc_repo: Path = Path("")
    seedvc_model_dir: Path = _DEFAULT_DATA_ROOT / "models" / "Seed-VC"

    @property
    def uploads(self) -> Path:
        return self.data_root / "uploads"

    @property
    def outputs(self) -> Path:
        return self.data_root / "outputs"

settings = Settings()
settings.uploads.mkdir(parents=True, exist_ok=True)
settings.outputs.mkdir(parents=True, exist_ok=True)
