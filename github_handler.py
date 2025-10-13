# github_handler.py
import requests
import json
import base64

def load_history(owner, repo, token, branch=None):
    """Loads history from GitHub, returns a list."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/history.json"
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
            print(f"Error loading history: {resp.status_code} - {resp.text}")
            return None # Indicate an error
    except Exception as e:
        print(f"An exception occurred while loading history: {e}")
        return None

def save_history(history, owner, repo, token, branch=None):
    """Saves history to GitHub, returns True on success, False on failure."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/history.json"
    if branch:
        url += f"?ref={branch}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    try:
        # Get current SHA if file exists
        resp_get = requests.get(url, headers=headers)
        sha = resp_get.json().get('sha') if resp_get.status_code == 200 else None

        # Prepare payload
        new_content = base64.b64encode(json.dumps(history, indent=4).encode('utf-8')).decode('utf-8')
        data = {"message": "Update LLM history", "content": new_content}
        if sha:
            data["sha"] = sha
        
        # Commit the file
        resp_put = requests.put(url, headers=headers, json=data)
        if resp_put.status_code in (200, 201):
            return True
        else:
            print(f"Error saving history: {resp_put.status_code} - {resp_put.text}")
            return False
    except Exception as e:
        print(f"An exception occurred while saving history: {e}")
        return False