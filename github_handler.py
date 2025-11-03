# github_handler.py
import requests
import json
import base64

def load_history(owner, repo, token, branch=None, file_path='history.json'):
    """Loads history from a specific file on GitHub, returns a list or an error message string."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    if branch:
        url += f"?ref={branch}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            content = base64.b64decode(resp.json()['content']).decode('utf-8')
            return json.loads(content)
        elif resp.status_code == 404:
            return []  # File doesn't exist yet, return empty history
        else:
            return f"Error loading history from {file_path}: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"An exception occurred while loading history from {file_path}: {e}"

def save_history(history, owner, repo, token, branch=None, file_path='history.json'):
    """Saves history to a specific file on GitHub, returns True on success, or an error message string on failure."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    if branch:
        url += f"?ref={branch}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    try:
        # Get current SHA if file exists
        resp_get = requests.get(url, headers=headers)
        sha = resp_get.json().get('sha') if resp_get.status_code == 200 else None

        # Prepare payload
        message = f"Update history for {file_path}"
        new_content = base64.b64encode(json.dumps(history, indent=4).encode('utf-8')).decode('utf-8')
        data = {"message": message, "content": new_content}
        if sha:
            data["sha"] = sha
        
        # Commit the file
        resp_put = requests.put(url, headers=headers, json=data)
        if resp_put.status_code in (200, 201):
            return True
        else:
            return f"Error saving history to {file_path}: {resp_put.status_code} - {resp_put.text}. URL: {url}, SHA: {sha}"
    except Exception as e:
        return f"An exception occurred while saving history to {file_path}: {e}"