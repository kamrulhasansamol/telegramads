# code.py
import aiohttp
from fastapi import FastAPI, HTTPException, Request
import random
import base64
import json

app = FastAPI()

# ================== SETTINGS ==================
GITHUB_USER = "YOUR_GITHUB_USERNAME"
GITHUB_REPO = "YOUR_REPO_NAME"
GITHUB_JSON_PATH = "codes.json"
GITHUB_TOKEN = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"

SECRET_KEY = "XenoSecret2025!"  # <-- secret key, keep it safe

# ================== HELPERS ==================
async def fetch_codes():
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{GITHUB_JSON_PATH}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("codes", [])
            else:
                raise HTTPException(status_code=500, detail="Failed to fetch codes from GitHub")

async def update_github_codes(codes_list, commit_message="Update codes"):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_JSON_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=500, detail="Failed to get file SHA from GitHub")
            data = await resp.json()
            sha = data["sha"]

        new_content = json.dumps({"codes": codes_list}, indent=2)
        encoded_content = base64.b64encode(new_content.encode()).decode()

        payload = {"message": commit_message, "content": encoded_content, "sha": sha}

        async with session.put(url, headers=headers, json=payload) as resp2:
            if resp2.status not in [200, 201]:
                raise HTTPException(status_code=500, detail="Failed to update codes on GitHub")
            return True

# ================== API ENDPOINT ==================
@app.get("/getcode")
async def get_code(request: Request):
    key = request.query_params.get("key")
    if key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    codes = await fetch_codes()
    if not codes:
        raise HTTPException(status_code=404, detail="No codes available")

    code = random.choice(codes)
    codes.remove(code)
    await update_github_codes(codes, commit_message=f"Code {code} used")
    return {"code": code}
