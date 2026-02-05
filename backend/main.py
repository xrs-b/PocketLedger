from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PocketLedger API",
    description="轻量级情侣记账应用 API",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "PocketLedger API", "status": "healthy"}


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
