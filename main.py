from fastapi import FastAPI, BackgroundTasks, Request, UploadFile, File
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import os
import json
import shutil

from cv_parser import extract_text_from_pdf
from llm_matcher import summarize_cv, score_job, analyze_cv_for_params
from scraper import LinkedInScraper

class StartScrapingRequest(BaseModel):
    roles: list
    location: str
    summary: str

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state to keep track of the scraping job
job_state = {
    "status": "idle", # idle, running, finished, error
    "logs": [],
    "results": [],
    "progress": 0
}

def log_msg(msg):
    print(msg)
    job_state["logs"].append(msg)

async def run_scraping_job(roles: list, location: str, summary: str):
    global job_state
    job_state["status"] = "running"
    job_state["logs"] = []
    job_state["results"] = []
    job_state["progress"] = 0
    
    try:
        log_msg(f"Starting multi-role job for: {', '.join(roles)} in {location}")
        job_state["progress"] = 10
        
        all_jobs = []
        scraper = LinkedInScraper()
        
        # Scrape 5 jobs for each role
        for idx, role in enumerate(roles):
            log_msg(f"Searching LinkedIn for role {idx+1}/{len(roles)}: {role}")
            jobs = await scraper.scrape_jobs(keywords=role, location=location, max_jobs=5, log_cb=log_msg)
            log_msg(f"Found {len(jobs)} jobs for {role}.")
            all_jobs.extend(jobs)
            job_state["progress"] = 10 + int(((idx + 1) / len(roles)) * 40)
            
        log_msg(f"Total jobs scraped: {len(all_jobs)}. Analyzing with AI...")
        
        # Deduplicate jobs by URL to prevent scoring the same job twice
        unique_jobs = {job["url"]: job for job in all_jobs}.values()
        unique_jobs = list(unique_jobs)
        log_msg(f"Total unique jobs to analyze: {len(unique_jobs)}")
        
        # Score Jobs
        scored_jobs = []
        for i, job in enumerate(unique_jobs):
            log_msg(f"Scoring job {i+1}/{len(unique_jobs)}: {job['title']} at {job['company']}")
            if not job["description"]:
                log_msg(f"Skipping {job['title']} due to missing description.")
                continue
                
            score_data = await asyncio.to_thread(
                score_job, summary, job["title"], job["description"]
            )
            
            job["score"] = score_data.get("score", 0)
            job["explanation"] = score_data.get("explanation", "No explanation.")
            scored_jobs.append(job)
            
            job_state["progress"] = 50 + int((i / len(unique_jobs)) * 50)
            
        # Filter and Sort Top 20
        scored_jobs.sort(key=lambda x: x["score"], reverse=True)
        top_20 = scored_jobs[:20]
        
        job_state["results"] = top_20
        job_state["progress"] = 100
        job_state["status"] = "finished"
        log_msg("Job completed successfully!")
        
    except Exception as e:
        log_msg(f"Error: {str(e)}")
        job_state["status"] = "error"


@app.get("/")
def serve_ui():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/analyze_cv")
async def analyze_cv(file: UploadFile = File(...)):
    temp_path = "uploaded_cv.pdf"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    cv_text = extract_text_from_pdf(temp_path)
    # Get parameters using Ollama
    params = await asyncio.to_thread(analyze_cv_for_params, cv_text)
    return JSONResponse(params)

@app.post("/api/start")
async def start_job(request: StartScrapingRequest, background_tasks: BackgroundTasks):
    if job_state["status"] == "running":
        return JSONResponse({"status": "already running"})
        
    background_tasks.add_task(run_scraping_job, request.roles, request.location, request.summary)
    return JSONResponse({"status": "started"})

@app.get("/api/status")
def get_status():
    return JSONResponse(job_state)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
