from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aiohttp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CUSTOM_HEADERS = {
    "X-API-KEY": "samol_kavach_4f8e2b7c9a1d4e6f8b2c3d5e7f9a0b1c",
    "X-CLIENT-ID": "cli_xeno_01F8MECHZX3TBDSZ7XRADM79XE",
    "User-Agent": "samol/1.0.0",
    "X-REQUEST-TYPE": "xeno-like"
}

async def make_like_request(uid, region):
    try:
        params = {"uid": uid, "region": region.upper()}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://newlike.vercel.app/like",
                params=params,
                headers=CUSTOM_HEADERS,
                timeout=15
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {"status": 0, "message": f"API Error {response.status}"}
    except:
        return {"status": 0, "message": "Network or API error"}

@app.get("/api/like")
async def like(uid: str, region: str):
    return await make_like_request(uid, region)
