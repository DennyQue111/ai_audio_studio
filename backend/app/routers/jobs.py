from fastapi import APIRouter

from ..jobs import download_job, download_job_output, get_job

router = APIRouter()


@router.get("/api/jobs/{job_id}")
def read_job(job_id: str):
    return get_job(job_id)


@router.get("/api/jobs/{job_id}/outputs/{index}/download")
def read_job_output(job_id: str, index: int):
    return download_job_output(job_id, index)


@router.get("/api/jobs/{job_id}/download")
def download(job_id: str):
    return download_job(job_id)
