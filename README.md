# Automated LLM Code Deployment System

This project is an automated system developed for the "Tools in Data Science" (TDM) course at IITM BS. It is designed to receive a task brief via a secure API endpoint, use the Google Gemini LLM to generate the required code, and automatically create, deploy, and update the resulting web application on GitHub Pages.

---

## 🚀 Core Features

- **Automated Build Process (Round 1):** Receives a brief, generates code, creates a new GitHub repository, adds an MIT license, pushes the code, and deploys it to GitHub Pages.
- **Automated Revise Process (Round 2):** Fetches existing code from a repository, uses an LLM to modify it based on a new brief, and pushes the update.
- **Secure Endpoint:** Uses a shared secret to validate all incoming requests.
- **Asynchronous Task Handling:** Utilizes FastAPI's `BackgroundTasks` to handle long-running processes without blocking the server.
- **Resilient Communication:** Includes exponential backoff retry logic for notifying the evaluation server.

---

## 🛠️ Architecture & Tools

This system is built with a modern Python stack:

- **Web Framework:** **FastAPI** with **Uvicorn** for creating a high-performance, asynchronous API server.
- **Large Language Model (LLM):** **Google Gemini API** (`gemini-pro-latest`) for code generation and modification.
- **Version Control & Deployment:** **GitHub API** (via the `PyGithub` library) for all repository and file management. **GitHub Pages** is used for hosting the final web applications.
- **Environment Management:** **Python `venv`** for dependency isolation and **`python-dotenv`** for secure management of API keys and secrets.

---

## ⚙️ Setup and Local Execution

To run this project on your local machine, follow these steps:

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone the Repository
```bash
git clone [https://github.com/V-Srikar/tds-llm-automation-server.git](https://github.com/V-Srikar/tds-llm-automation-server.git)
cd tds-llm-automation-server