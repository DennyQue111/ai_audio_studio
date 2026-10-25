import threading
import uuid
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse

from .config import settings

jobs = {}


def submit(kind, fn):
    job_id = uuid.uuid4().hex
    jobs[job_id] = {"id": job_id, "kind": kind, "status": "queued", "message": "等待执行"}

    def work():
        jobs[job_id].update(status="running", message="模型处理中")
        try:
            output = fn()
            if isinstance(output, dict):
                output_files = [{"name": name, "path": str(path)} for name, path in output.items()]
                outputs = [
                    {
                        "name": item["name"],
                        "download": f"/api/jobs/{job_id}/outputs/{index}/download",
                    }
                    for index, item in enumerate(output_files)
                ]
                jobs[job_id].update(
                    status="completed",
                    message="处理完成",
                    outputs=outputs,
                    _output_files=output_files,
                )
            else:
                jobs[job_id].update(
                    status="completed",
                    message="处理完成",
                    output=str(output),
                    download=f"/api/jobs/{job_id}/download",
                )
        except Exception as exc:
            jobs[job_id].update(status="failed", message="处理失败", error=str(exc))

    threading.Thread(target=work, daemon=True).start()
    return {"job_id": job_id}


def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "任务不存在")
    return {key: value for key, value in jobs[job_id].items() if not key.startswith("_")}


def download_job_output(job_id: str, index: int):
    output_files = jobs.get(job_id, {}).get("_output_files", [])
    if index < 0 or index >= len(output_files):
        raise HTTPException(404, "结果不存在")
    path = Path(output_files[index]["path"])
    if not path.is_file():
        raise HTTPException(404, "结果不存在")
    return FileResponse(path, filename=path.name)


def download_job(job_id: str):
    path = Path(jobs.get(job_id, {}).get("output", ""))
    if not path.is_file():
        raise HTTPException(404, "结果不存在")
    return FileResponse(path, filename=path.name)
