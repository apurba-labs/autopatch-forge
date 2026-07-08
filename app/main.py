from fastapi import FastAPI
import uvicorn
from app.api.routes import router

app = FastAPI(title="AutoPatch Forge Platform", version="1.2.0")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)