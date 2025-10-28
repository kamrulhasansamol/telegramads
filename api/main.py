from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import os
import json

app = FastAPI()

# Allow CORS for local testing or any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directory (optional)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

# Like API settings
LIKE_API_URL = "https://newlike.vercel.app/like"
CUSTOM_HEADERS = {
    "X-API-KEY": "samol_kavach_4f8e2b7c9a1d4e6f8b2c3d5e7f9a0b1c",
    "X-CLIENT-ID": "cli_xeno_01F8MECHZX3TBDSZ7XRADM79XE",
    "User-Agent": "samol/1.0.0",
    "X-REQUEST-TYPE": "xeno-like"
}

# Call the external like API
async def make_like_request(uid, region):
    try:
        params = {"uid": uid, "region": region.upper()}
        async with aiohttp.ClientSession() as session:
            async with session.get(LIKE_API_URL, params=params, headers=CUSTOM_HEADERS, timeout=15) as response:
                text = await response.text()
                print("DEBUG: API response:", text)  # <--- debug output
                if response.status == 200:
                    return await response.json()
                return {"status": 0, "message": f"API Error {response.status}", "raw": text}
    except Exception as e:
        return {"status": 0, "message": "Network or API error", "error": str(e)}

# Direct API route (optional)
@app.get("/api/like")
async def like(uid: str, region: str, user_id: str = ""):
    res = await make_like_request(uid, region)
    return res

# Callback route after ad completes
@app.get("/afterad")
async def afterad(request: Request):
    params = request.query_params
    uid = params.get("uid", "")
    region = params.get("region", "AG")
    user_id = params.get("user_id", "")

    if not uid:
        html = "<h2>Missing UID</h2><p>No UID provided.</p>"
        return Response(content=html, media_type="text/html")

    # Call like API
    res = await make_like_request(uid, region)

    # Build result HTML
    if res.get("status") == 1:
        player = res.get("player", {})
        likes = res.get("likes", {})
        html = f"""
        <html>
        <head><meta charset='utf-8'><title>Like Result</title>
        <style>body{{background:#0f172a;color:#fff;font-family:Arial;padding:24px}} .card{{background:#111827;padding:20px;border-radius:10px;max-width:600px;margin:40px auto}} .ok{{color:#34d399}}</style>
        </head>
        <body>
          <div class='card'>
            <h2 class='ok'>✅ Like Added Successfully</h2>
            <p><strong>Player:</strong> {player.get('nickname','N/A')} ({player.get('uid', uid)})</p>
            <p><strong>Region:</strong> {player.get('region', region)}</p>
            <p><strong>Before:</strong> {likes.get('before','N/A')} &nbsp; <strong>Added:</strong> {likes.get('added_by_api','N/A')} &nbsp; <strong>Total:</strong> {likes.get('after','N/A')}</p>
            <p style='margin-top:12px'><a href='/' style='color:#60a5fa'>Back to tool</a></p>
          </div>
        </body>
        </html>
        """
    else:
        message = res.get("message", "Like failed or API error")
        html = f"""
        <html>
        <head><meta charset='utf-8'><title>Like Failed</title>
        <style>body{{background:#0f172a;color:#fff;font-family:Arial;padding:24px}} .card{{background:#111827;padding:20px;border-radius:10px;max-width:600px;margin:40px auto}} .err{{color:#f87171}}</style>
        </head>
        <body>
          <div class='card'>
            <h2 class='err'>⚠️ Like Failed</h2>
            <p>{message}</p>
            <p style='margin-top:12px'><a href='/' style='color:#60a5fa'>Back to tool</a></p>
          </div>
        </body>
        </html>
        """
    return Response(content=html, media_type="text/html")
