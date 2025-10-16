# worker.py
import os
import httpx
import time
import base64
import google.generativeai as genai
from github import Github, GithubException

# --- FUNCTION 1: CREATE REPO ---
def create_github_repo(repo_name: str, pat: str):
    """Creates a new public repository on GitHub."""
    try:
        g = Github(pat)
        user = g.get_user()
        print(f"Creating new repository: {repo_name}...")
        repo = user.create_repo(
            name=repo_name,
            private=False,
            auto_init=True,
            license_template='mit'
        )
        print(f"✅ Successfully created repository: {repo.html_url}")
        return repo
    except GithubException as e:
        if e.status == 422 and "name already exists" in str(e.data):
            print(f"⚠️ Repository '{repo_name}' already exists. Re-using it.")
            return user.get_repo(repo_name)
        else:
            print(f"❌ An error occurred with GitHub API: {e}")
            return None

# --- FUNCTION 2: PUSH FILE ---
def push_file_to_repo(repo, file_path: str, commit_message: str, content: str):
    """Pushes a file to the repo, creating it if it doesn't exist or updating it if it does."""
    try:
        print(f"Pushing file '{file_path}' to repo '{repo.name}'...")
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        try:
            # Check if file exists to get its SHA for updating
            existing_file = repo.get_contents(file_path, ref="main")
            print(f"⚠️ File '{file_path}' already exists. Updating it.")
            result = repo.update_file(
                path=existing_file.path,
                message=commit_message,
                content=encoded_content,
                sha=existing_file.sha,
                branch="main"
            )
        except GithubException as e:
            if e.status == 404: # File does not exist, so create it
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=encoded_content,
                    branch="main"
                )
            else:
                raise e # Re-raise other GitHub errors

        commit_sha = result['commit'].sha
        print(f"✅ Successfully pushed {file_path}. Commit SHA: {commit_sha}")
        return commit_sha, True

    except GithubException as e:
        print(f"❌ An error occurred while pushing file: {e}")
        return None, False

# --- FUNCTION 3: GET EXISTING CODE ---
def get_existing_code(repo, file_path: str):
    """Fetches the content of a file from a GitHub repository."""
    try:
        print(f"Fetching existing code for '{file_path}' from repo '{repo.name}'...")
        file_content = repo.get_contents(file_path, ref="main")
        decoded_content = base64.b64decode(file_content.content).decode('utf-8')
        print("✅ Successfully fetched existing code.")
        return decoded_content
    except GithubException as e:
        if e.status == 404:
            print(f"❌ Could not find file '{file_path}' in the repository.")
        else:
            print(f"❌ An error occurred while fetching the file: {e}")
        return None

# --- FUNCTION 4: GENERATE CODE WITH LLM ---
def generate_code_with_llm(brief: str, checks: list, attachments: list, existing_code: str | None):
    """Uses the Gemini API to generate or modify HTML code, including checks and attachments."""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-pro-latest')

        full_prompt = "You are an expert web developer. Your task is to generate a complete, single-file HTML document.\n"
        full_prompt += "The HTML file must include all necessary CSS and JavaScript embedded within it.\n"
        full_prompt += "Do not include any explanations, comments, or any text outside of the HTML code itself.\n\n"

        if existing_code:
            full_prompt += f"--- EXISTING HTML CODE ---\n{existing_code}\n--- END OF EXISTING CODE ---\n\n"
            full_prompt += f"--- NEW BRIEF TO IMPLEMENT ---\n\"{brief}\"\n--- END OF NEW BRIEF ---\n\n"
            print(f"Generating revised code with LLM for brief: {brief}...")
        else:
            full_prompt += f"Brief: \"{brief}\"\n\n"
            print(f"Generating new code with LLM for brief: {brief}...")

        if checks:
            full_prompt += "Your generated code will be evaluated against the following checks:\n"
            for check in checks:
                full_prompt += f"- {check}\n"
            full_prompt += "\n"

        if attachments:
            full_prompt += "The following files are attached. Use their content as required by the brief:\n"
            for attachment in attachments:
                file_name = attachment.get('name')
                data_uri = attachment.get('url')
                try:
                    content_string = data_uri.split(',')[1]
                    decoded_content = base64.b64decode(content_string).decode('utf-8')
                    full_prompt += f"- File Name: {file_name}\n- Content:\n```\n{decoded_content}\n```\n"
                except Exception as e:
                    print(f"Warning: Could not decode attachment {file_name}. Error: {e}")
            full_prompt += "\n"
        
        request_options = {"timeout": 120}
        response = model.generate_content(full_prompt, request_options=request_options)
        
        print("✅ LLM code generation complete.")
        return response.text
        
    except Exception as e:
        print(f"❌ An error occurred with the Gemini API: {e}")
        return None

# --- FUNCTION 5: ENABLE GITHUB PAGES ---
def enable_github_pages(repo, pat: str):
    """Enables GitHub Pages for the specified repository."""
    try:
        print(f"Enabling GitHub Pages for repo '{repo.name}'...")
        headers = {
            "Authorization": f"Bearer {pat}",
            "Accept": "application/vnd.github.v3+json"
        }
        pages_api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/pages"
        pages_payload = {
            "build_type": "legacy",
            "source": {"branch": "main", "path": "/"}
        }
        response = httpx.post(pages_api_url, headers=headers, json=pages_payload)
        response.raise_for_status()
        print(f"✅ GitHub Pages enabled successfully. It may take a minute to go live.")
        return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
             print(f"⚠️ GitHub Pages seems to be already enabled for '{repo.name}'.")
             return True
        print(f"❌ An error occurred enabling GitHub Pages: {e}")
        return False

# --- FUNCTION 6: PING EVALUATION SERVER ---
def ping_evaluation_server(data: dict, repo_url: str, commit_sha: str, pages_url: str):
    """Pings the evaluation_url with the project details and handles retries."""
    payload = {
        "email": data['email'], "task": data['task'], "round": data['round'],
        "nonce": data['nonce'], "repo_url": repo_url, "commit_sha": commit_sha,
        "pages_url": pages_url
    }
    evaluation_url = data['evaluation_url']
    print(f"Pinging evaluation server at: {evaluation_url}...")
    retries = 4
    delay = 1
    for i in range(retries):
        try:
            with httpx.Client() as client:
                response = client.post(evaluation_url, json=payload, timeout=20.0)
                response.raise_for_status()
                print("✅ Successfully pinged evaluation server.")
                return True
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            print(f"❌ Ping attempt {i+1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
    
    print("❌ Failed to ping evaluation server after all retries.")
    return False