from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional  # ← Add this import
from gee_service import get_satellite_image
from analysis import analyze_project_status

app = FastAPI(title="Ghost Project Hunter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://integrity-lens-favour.vercel.app",  # <--- ADD THIS EXACT LINE
        "https://integrity-lens-favour.vercel.app/"  # <--- Add with slash too just in case
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProjectRequest(BaseModel):
    project_id: str
    latitude: float
    longitude: float
    project_type: str
    contract_date: Optional[str] = None  # ← Change this line to make it optional

@app.get("/")
def read_root():
    return {"status": "System Operational", "module": "Vertical C: Infrastructure Verification"}

@app.post("/verify")
def verify_project(request: ProjectRequest):
    """
    Endpoint to verify a project site.
    """
    try:
        date_from = "2025-09-01" 
        date_to = "2025-12-01"

        print(f"Fetching satellite data for {request.project_id}...")
        satellite_data = get_satellite_image(
            request.latitude, 
            request.longitude, 
            date_from, 
            date_to
        )

        report = analyze_project_status(request.project_type, satellite_data)

        return {
            "project_id": request.project_id,
            "location": {"lat": request.latitude, "lon": request.longitude},
            "satellite_analysis": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)