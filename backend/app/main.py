from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import audio, features, generation, jobs, speech, system

app = FastAPI(title="AI Audio Studio")
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

for router in (system.router, jobs.router, speech.router, generation.router, audio.router, features.router):
    app.include_router(router)
