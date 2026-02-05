from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine, get_db
from app import models

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


# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
def read_root():
    return {"message": "PocketLedger API", "status": "healthy"}


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
