"""ComfyUI status checks and API-format workflows used by the web app."""

from __future__ import annotations

import json
import random
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .config import settings

QWEN_NODE = "FB_Qwen3TTSVoiceDesign"
T5GEMMA_FILE = "t5gemma_b_b_ul2.safetensors"
STABLE_AUDIO_MAX_SECONDS = 120


def _request_json(path: str, *, payload: dict[str, Any] | None = None, timeout: float = 10) -> Any:
    url = settings.comfyui_url.rstrip("/") + path
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[-2000:]
        raise RuntimeError(f"ComfyUI 返回 HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"无法连接 ComfyUI ({settings.comfyui_url}): {exc}") from exc


def _valid_model(path: Path) -> bool:
    try:
        return path.is_file() and path.stat().st_size > 1_000_000
    except OSError:
        return False


def status() -> dict[str, Any]:
    root = settings.comfyui_root
    qwen_model = root / "models" / "qwen-tts" / "Qwen3-TTS-12Hz-1.7B-VoiceDesign"
    qwen_missing = []
    qwen_node = root / "custom_nodes" / "qwen3-tts-comfyui" / "__init__.py"
    if not qwen_node.is_file():
        qwen_missing.append(str(qwen_node.relative_to(root)))
    for model_file in (qwen_model / "model.safetensors", qwen_model / "speech_tokenizer" / "model.safetensors"):
        if not _valid_model(model_file):
            qwen_missing.append(str(model_file.relative_to(root)))

    site_packages = root.parent / "python_embeded" / "Lib" / "site-packages"
    for module in ("librosa", "soundfile", "tiktoken", "onnxruntime", "sox"):
        if not (site_packages / module).exists() and not (site_packages / f"{module}.py").is_file():
            qwen_missing.append(f"python_embeded/Lib/site-packages/{module}")

    encoder = root / "models" / "text_encoders" / T5GEMMA_FILE
    music = root / "models" / "checkpoints" / "stable_audio_3_small_music.safetensors"
    sfx = root / "models" / "checkpoints" / "stable_audio_3_small_sfx.safetensors"
    encoder_missing = [] if _valid_model(encoder) else [str(encoder.relative_to(root))]
    music_missing = encoder_missing + ([] if _valid_model(music) else [str(music.relative_to(root))])
    sfx_missing = encoder_missing + ([] if _valid_model(sfx) else [str(sfx.relative_to(root))])

    try:
        _request_json("/system_stats", timeout=5)
        online = True
        connection_error = None
    except RuntimeError as exc:
        online = False
        connection_error = str(exc)

    try:
        separation_node_ready = "AudioSeparation" in _request_json(
            "/object_info/AudioSeparation", timeout=5
        )
    except RuntimeError:
        separation_node_ready = False

    return {
        "url": settings.comfyui_url,
        "online": online,
        "connection_error": connection_error,
        "qwen_voice_design_ready": not qwen_missing and online,
        "qwen_voice_design_missing": qwen_missing,
        "audio_separation_ready": online and separation_node_ready,
        "stable_audio_music_ready": not music_missing and online,
        "stable_audio_sfx_ready": not sfx_missing and online,
        "stable_audio_music_missing": music_missing,
        "stable_audio_sfx_missing": sfx_missing,
        "stable_audio_missing": sorted(set(music_missing + sfx_missing)),
        "model_root": str(root),
    }


def voice_design_workflow(text: str, description: str, save_prefix: str) -> dict[str, Any]:
    return {
        "1": {
            "class_type": QWEN_NODE,
            "inputs": {
                "text": text,
                "instruct": description,
                "model_choice": "1.7B",
                "device": "auto",
                "precision": "bf16",
                "language": "Chinese",
                "seed": random.randrange(0, 2**32),
                "max_new_tokens": 2048,
                "top_p": 0.8,
                "top_k": 20,
                "temperature": 1.0,
                "repetition_penalty": 1.05,
                "attention": "sdpa",
                "unload_model_after_generate": True,
            },
        },
        "2": {
            "class_type": "SaveAudio",
            "inputs": {"audio": ["1", 0], "filename_prefix": save_prefix},
        },
    }


def stable_audio_workflow(
    prompt: str,
    category: str,
    duration: int,
    save_prefix: str,
) -> dict[str, Any]:
    if category not in {"music", "sfx"}:
        raise ValueError("category must be 'music' or 'sfx'")
    if not 1 <= duration <= STABLE_AUDIO_MAX_SECONDS:
        raise ValueError(f"duration must be between 1 and {STABLE_AUDIO_MAX_SECONDS} seconds")
    checkpoint = f"stable_audio_3_small_{category}.safetensors"
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": checkpoint}},
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": T5GEMMA_FILE,
                "type": "stable_audio",
                "device": "default",
            },
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 0], "text": prompt},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 0], "text": ""},
        },
        "5": {
            "class_type": "EmptyLatentAudio",
            "inputs": {"seconds": float(duration), "batch_size": 1},
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": random.randrange(0, 2**32),
                "steps": 8,
                "cfg": 1.0,
                "sampler_name": "lcm",
                "scheduler": "simple",
                "denoise": 1.0,
            },
        },
        "7": {
            "class_type": "VAEDecodeAudio",
            "inputs": {"samples": ["6", 0], "vae": ["1", 2]},
        },
        "8": {
            "class_type": "SaveAudio",
            "inputs": {"audio": ["7", 0], "filename_prefix": save_prefix},
        },
    }


def audio_separation_workflow(input_filename: str, save_prefix: str) -> dict[str, Any]:
    """Split a song into vocals, a combined backing track, and its 3 music stems."""
    return {
        "1": {"class_type": "LoadAudio", "inputs": {"audio": input_filename}},
        "2": {
            "class_type": "AudioSeparation",
            "inputs": {
                "audio": ["1", 0],
                "chunk_length": 10.0,
                "chunk_overlap": 0.1,
                "chunk_fade_shape": "linear",
            },
        },
        "3": {
            "class_type": "AudioCombine",
            "inputs": {"audio_1": ["2", 0], "audio_2": ["2", 1], "method": "add"},
        },
        "4": {
            "class_type": "AudioCombine",
            "inputs": {"audio_1": ["3", 0], "audio_2": ["2", 2], "method": "add"},
        },
        "5": {
            "class_type": "SaveAudio",
            "inputs": {"audio": ["2", 3], "filename_prefix": f"{save_prefix}/vocals"},
        },
        "6": {
            "class_type": "SaveAudio",
            "inputs": {"audio": ["4", 0], "filename_prefix": f"{save_prefix}/instrumental"},
        },
        "7": {
            "class_type": "SaveAudio",
            "inputs": {"audio": ["2", 0], "filename_prefix": f"{save_prefix}/bass"},
        },
        "8": {
            "class_type": "SaveAudio",
            "inputs": {"audio": ["2", 1], "filename_prefix": f"{save_prefix}/drums"},
        },
        "9": {
            "class_type": "SaveAudio",
            "inputs": {"audio": ["2", 2], "filename_prefix": f"{save_prefix}/other"},
        },
    }


def run_workflow(
    workflow: dict[str, Any],
    output_stem: str,
    timeout: float = 7200,
    output_nodes: dict[str, str] | None = None,
) -> Path | dict[str, Path]:
    response = _request_json("/prompt", payload={"prompt": workflow}, timeout=30)
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI 未接受工作流: {json.dumps(response, ensure_ascii=False)}")

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        history = _request_json(f"/history/{urllib.parse.quote(str(prompt_id), safe='')}", timeout=15)
        result = history.get(str(prompt_id))
        if result:
            run_status = result.get("status", {})
            if run_status.get("status_str") in {"error", "failed"}:
                raise RuntimeError(f"ComfyUI 工作流执行失败: {json.dumps(run_status, ensure_ascii=False)}")
            if run_status.get("completed"):
                if output_nodes:
                    paths = {}
                    for node_id, output_name in output_nodes.items():
                        node_output = result.get("outputs", {}).get(node_id, {})
                        audio_items = [
                            item
                            for values in node_output.values()
                            if isinstance(values, list)
                            for item in values
                            if isinstance(item, dict) and item.get("filename")
                        ]
                        if not audio_items:
                            raise RuntimeError(f"ComfyUI 已完成，但没有返回 {output_name} 音轨")
                        info = audio_items[-1]
                        extension = Path(info["filename"]).suffix.lower()
                        if extension not in {".wav", ".mp3", ".flac", ".ogg"}:
                            raise RuntimeError(f"ComfyUI 返回了不支持的音频格式: {extension}")
                        query = urllib.parse.urlencode(
                            {
                                "filename": info["filename"],
                                "subfolder": info.get("subfolder", ""),
                                "type": info.get("type", "output"),
                            }
                        )
                        request = urllib.request.Request(
                            settings.comfyui_url.rstrip("/") + "/view?" + query
                        )
                        try:
                            with urllib.request.urlopen(request, timeout=60) as audio_response:
                                audio_bytes = audio_response.read()
                        except (urllib.error.URLError, TimeoutError, OSError) as exc:
                            raise RuntimeError(f"无法从 ComfyUI 取回 {output_name} 音轨: {exc}") from exc
                        destination = settings.outputs / f"{output_stem}_{output_name}{extension}"
                        destination.write_bytes(audio_bytes)
                        paths[output_name] = destination
                    return paths

                output = result.get("outputs", {}).get("8") or result.get("outputs", {}).get("2") or {}
                audio_items = [item for values in output.values() if isinstance(values, list) for item in values if isinstance(item, dict) and item.get("filename")]
                if not audio_items:
                    raise RuntimeError("ComfyUI 已完成，但没有返回音频文件")
                info = audio_items[-1]
                extension = Path(info["filename"]).suffix.lower()
                if extension not in {".wav", ".mp3", ".flac", ".ogg"}:
                    raise RuntimeError(f"ComfyUI 返回了不支持的音频格式: {extension}")
                query = urllib.parse.urlencode(
                    {
                        "filename": info["filename"],
                        "subfolder": info.get("subfolder", ""),
                        "type": info.get("type", "output"),
                    }
                )
                request = urllib.request.Request(settings.comfyui_url.rstrip("/") + "/view?" + query)
                try:
                    with urllib.request.urlopen(request, timeout=60) as audio_response:
                        audio_bytes = audio_response.read()
                except (urllib.error.URLError, TimeoutError, OSError) as exc:
                    raise RuntimeError(f"无法从 ComfyUI 取回生成音频: {exc}") from exc
                destination = settings.outputs / f"{output_stem}{extension}"
                destination.write_bytes(audio_bytes)
                return destination
        time.sleep(1.5)

    raise RuntimeError("等待 ComfyUI 任务超时；任务可能仍在 ComfyUI 队列中")


def make_voice_design(text: str, description: str, job_id: str) -> Path:
    prefix = f"AI_Audio_Studio/{job_id}"
    workflow = voice_design_workflow(text, description, prefix)
    return run_workflow(workflow, f"voice_design_{job_id}")


def make_stable_audio(prompt: str, category: str, duration: int, job_id: str) -> Path:
    prefix = f"AI_Audio_Studio/{job_id}"
    workflow = stable_audio_workflow(prompt, category, duration, prefix)
    return run_workflow(workflow, f"stable_audio_{job_id}")


def make_audio_separation(source: Path, job_id: str) -> dict[str, Path]:
    if not settings.comfyui_root.is_dir():
        raise RuntimeError(f"ComfyUI 目录不存在: {settings.comfyui_root}")

    input_dir = settings.comfyui_root / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    input_filename = f"ai_audio_studio_{job_id}{source.suffix.lower()}"
    comfy_input = input_dir / input_filename
    shutil.copyfile(source, comfy_input)

    prefix = f"AI_Audio_Studio/{job_id}"
    workflow = audio_separation_workflow(input_filename, prefix)
    outputs = run_workflow(
        workflow,
        f"audio_separation_{job_id}",
        output_nodes={
            "5": "vocals",
            "6": "instrumental",
            "7": "bass",
            "8": "drums",
            "9": "other",
        },
    )
    if not isinstance(outputs, dict):
        raise RuntimeError("ComfyUI 未返回分离后的音轨")
    return outputs
