from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Unicornio Dev API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/v1/architect/analyze")
async def analyze(project_name: str, description: str):
    return {"project": project_name, "status": "Add CLAUDE_API_KEY to enable"}

@app.post("/api/v1/refactor/code")
async def refactor(code: str, language: str = "python"):
    return {"original": code[:50], "status": "Add CLAUDE_API_KEY to enable"}

@app.post("/api/v1/debug/solve")
async def debug(error: str, context: str = ""):
    return {"error": error[:50], "status": "Add CLAUDE_API_KEY to enable"}

@app.post("/api/v1/security/audit")
async def security(code: str):
    return {"status": "Add CLAUDE_API_KEY to enable"}

@app.post("/api/v1/performance/analyze")
async def performance(code: str):
    return {"status": "Add CLAUDE_API_KEY to enable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
