import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import graph, people, relationships

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Family Tree API")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(people.router)
app.include_router(relationships.router)
app.include_router(graph.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "family-tree-api"}
