from fastapi import APIRouter

from ..comfyui import status as comfy_status
from ..services import model_status

router = APIRouter()


@router.get("/api/models")
def models():
    state = model_status()
    state["comfyui"] = comfy_status()
    return state
