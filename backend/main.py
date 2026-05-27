from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.upload import router as upload_router
from routers.search import router as search_router


app = FastAPI(
    title="Internal Engineering Knowledge Search Platform",
    description="Search internal engineering documents using AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(search_router)

@app.get("/")
def root():
    return {"message": "Knowledge Search Platform is running"}

@app.get("/health")
def health():
    return {"status": "ok"}