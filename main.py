# main.py
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from dotenv import load_dotenv
import os
from github import Github

# Import all our worker functions
from worker import (
    create_github_repo, 
    push_file_to_repo, 
    generate_code_with_llm, 
    enable_github_pages, 
    ping_evaluation_server, 
    get_existing_code
)

load_dotenv()
app = FastAPI()

MY_PROJECT_SECRET = os.getenv("MY_PROJEC_SECRET")
GITHUB_PAT = os.getenv("GITHUB_PAT")


# --- BACKGROUND TASK FOR ROUND 1 ---
def process_build_request(data: dict):
    print("--- Background task started for Round 1 (Build) ---")
    user_login = "V-Srikar" # Your GitHub username
    repo_name = f"tds-app-{data['task']}"
    
    repo = create_github_repo(repo_name, GITHUB_PAT)
    if not repo: return

    html_content = generate_code_with_llm(
        brief=data['brief'], 
        checks=data.get('checks', []), 
        attachments=data.get('attachments', []),
        existing_code=None
    )
    if not html_content: return

    commit_sha, push_success = push_file_to_repo(
        repo=repo,
        file_path="index.html",
        commit_message="Round 1: Initial commit of AI-generated code",
        content=html_content
    )
    if not push_success: return
        
    pages_enabled = enable_github_pages(repo, GITHUB_PAT)
    if not pages_enabled: return

    pages_url = f"https://{user_login}.github.io/{repo_name}/"
    ping_evaluation_server(data, repo.html_url, commit_sha, pages_url)
    print(f"✅ Background task (Round 1) fully completed for repo: {repo.html_url}")


# --- BACKGROUND TASK FOR ROUND 2 ---
def process_revise_request(data: dict):
    print(f"--- Background task started for Round 2 (Revise) on task: {data['task']} ---")
    user_login = "V-Srikar" # Your GitHub username
    repo_name = f"tds-app-{data['task']}"

    try:
        g = Github(GITHUB_PAT)
        user = g.get_user()
        repo = user.get_repo(repo_name)
    except Exception as e:
        print(f"❌ Failed to get repository '{repo_name}'. Error: {e}")
        return

    existing_code = get_existing_code(repo, "index.html")
    if not existing_code: return

    revised_content = generate_code_with_llm(
        brief=data['brief'], 
        checks=data.get('checks', []), 
        attachments=data.get('attachments', []),
        existing_code=existing_code
    )
    if not revised_content: return

    commit_sha, push_success = push_file_to_repo(
        repo=repo,
        file_path="index.html",
        commit_message="Round 2: Update code based on new brief",
        content=revised_content
    )
    if not push_success: return

    pages_url = f"https://{user_login}.github.io/{repo_name}/"
    ping_evaluation_server(data, repo.html_url, commit_sha, pages_url)
    print(f"✅ Background task (Round 2) fully completed for repo: {repo.html_url}")


# --- MAIN API ENDPOINT ---
@app.post("/handle-task")
async def handle_task_request(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if data.get('secret') != MY_PROJECT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    if data.get('round') == 1:
        background_tasks.add_task(process_build_request, data)
        return {"message": "Request for Round 1 (Build) received. Process started in the background."}
    elif data.get('round') == 2:
        background_tasks.add_task(process_revise_request, data)
        return {"message": "Request for Round 2 (Revise) received. Process started in the background."}
    else:
        raise HTTPException(status_code=400, detail="Invalid round number. Must be 1 or 2.")